import pytest
from app.schemas import (
    KpiSnapshot,
    BusinessProfile,
    GrowthGoal,
    FunnelInsight,
    GrowthExperiment,
)
from app.logic import (
    diagnose_funnel,
    propose_experiments,
    score_experiments_ice,
    generate_copy,
    build_growth_plan,
)


class TestFunnelDiagnosis:
    """Test funnel analysis across all bottleneck scenarios"""

    def test_diagnose_visits_to_leads_bottleneck(self):
        """Largest drop from visits to leads"""
        kpis = KpiSnapshot(
            visits=1000,
            leads=100,  # 90% drop
            signups=80,
            purchases=60,
            revenue=6000.0,
        )
        insight = diagnose_funnel(kpis)

        assert insight.from_step == "visits"
        assert insight.to_step == "leads"
        assert insight.drop_rate == 0.9
        assert "visits to leads" in insight.comment.lower()

    def test_diagnose_leads_to_signups_bottleneck(self):
        """Largest drop from leads to signups"""
        kpis = KpiSnapshot(
            visits=1000,
            leads=800,
            signups=100,  # 87.5% drop
            purchases=80,
            revenue=8000.0,
        )
        insight = diagnose_funnel(kpis)

        assert insight.from_step == "leads"
        assert insight.to_step == "signups"
        assert insight.drop_rate == 0.875

    def test_diagnose_signups_to_purchases_bottleneck(self):
        """Largest drop from signups to purchases"""
        kpis = KpiSnapshot(
            visits=1000,
            leads=800,
            signups=600,
            purchases=50,  # 91.7% drop
            revenue=5000.0,
        )
        insight = diagnose_funnel(kpis)

        assert insight.from_step == "signups"
        assert insight.to_step == "purchases"
        assert round(insight.drop_rate, 2) == 0.92

    def test_diagnose_handles_zero_values(self):
        """Handle edge case with zero denominator"""
        kpis = KpiSnapshot(
            visits=0,
            leads=0,
            signups=0,
            purchases=0,
            revenue=0.0,
        )
        insight = diagnose_funnel(kpis)

        # Should not crash, should return a valid insight
        assert insight.from_step is not None
        assert insight.to_step is not None
        assert insight.drop_rate >= 0


class TestExperimentProposal:
    """Test experiment generation for all bottleneck types"""

    def test_propose_experiments_visits_to_leads(self):
        """Visits→Leads bottleneck generates appropriate experiments"""
        business = BusinessProfile(
            business_id="test_001",
            name="Test Business",
            industry="Retail",
            region="Toronto",
        )
        goal = GrowthGoal(objective="increase leads", horizon_weeks=4)
        insight = FunnelInsight(
            from_step="visits",
            to_step="leads",
            drop_rate=0.8,
            comment="Big drop",
        )

        experiments = propose_experiments(business, goal, insight)

        assert len(experiments) >= 2
        experiment_names = [e.name.lower() for e in experiments]
        # Should propose lead generation experiments
        assert any("lead" in name or "referral" in name for name in experiment_names)

    def test_propose_experiments_leads_to_signups(self):
        """Leads→Signups bottleneck generates appropriate experiments"""
        business = BusinessProfile(
            business_id="test_002",
            name="Test SaaS",
            industry="Technology",
            region="Boston",
        )
        goal = GrowthGoal(objective="increase signups", horizon_weeks=8)
        insight = FunnelInsight(
            from_step="leads",
            to_step="signups",
            drop_rate=0.7,
            comment="Conversion issue",
        )

        experiments = propose_experiments(business, goal, insight)

        assert len(experiments) >= 2
        experiment_names = [e.name.lower() for e in experiments]
        # Should propose signup conversion experiments
        assert any(
            "onboarding" in name or "demo" in name or "nurture" in name
            for name in experiment_names
        )

    def test_propose_experiments_signups_to_purchases(self):
        """Signups→Purchases bottleneck generates appropriate experiments"""
        business = BusinessProfile(
            business_id="test_003",
            name="Test Store",
            industry="E-commerce",
            region="NYC",
        )
        goal = GrowthGoal(objective="increase purchases", horizon_weeks=6)
        insight = FunnelInsight(
            from_step="signups",
            to_step="purchases",
            drop_rate=0.85,
            comment="Purchase barrier",
        )

        experiments = propose_experiments(business, goal, insight)

        assert len(experiments) >= 2
        experiment_names = [e.name.lower() for e in experiments]
        # Should propose purchase conversion experiments
        assert any("loyalty" in name or "win-back" in name for name in experiment_names)

    def test_propose_experiments_fallback(self):
        """Unknown bottleneck still returns experiments"""
        business = BusinessProfile(
            business_id="test_004",
            name="Test",
            industry="Other",
            region="Test",
        )
        goal = GrowthGoal(objective="grow", horizon_weeks=4)
        insight = FunnelInsight(
            from_step="unknown",
            to_step="other",
            drop_rate=0.5,
            comment="Test",
        )

        experiments = propose_experiments(business, goal, insight)

        # Should still return at least 1 experiment (fallback)
        assert len(experiments) >= 1


class TestICEScoring:
    """Test ICE prioritization across all experiment types"""

    def test_ice_scoring_calculates_correctly(self):
        """Priority score = (Impact × Confidence) / Effort"""
        experiments = [
            GrowthExperiment(
                name="Test Experiment",
                channel="email",
                hypothesis="This will work",
            )
        ]

        scored = score_experiments_ice(experiments)

        assert len(scored) == 1
        exp = scored[0]
        # Verify ICE formula
        expected_score = (exp.impact * exp.confidence) / exp.effort
        assert exp.priority_score == expected_score

    def test_ice_scoring_ranks_by_priority(self):
        """Higher priority experiments come first"""
        experiments = [
            GrowthExperiment(
                name="Low Priority",
                channel="events",  # High effort
                hypothesis="Test",
            ),
            GrowthExperiment(
                name="High Priority Referral",
                channel="email",  # Low effort
                hypothesis="Referral program",
            ),
        ]

        scored = score_experiments_ice(experiments)

        # Should be sorted by priority_score descending
        for i in range(len(scored) - 1):
            assert scored[i].priority_score >= scored[i + 1].priority_score

    def test_ice_scoring_all_experiment_types(self):
        """All experiment types get scored appropriately"""
        experiments = [
            GrowthExperiment(name="Referral Program", channel="email", hypothesis="Test"),
            GrowthExperiment(name="Loyalty Punch Card", channel="in-store", hypothesis="Test"),
            GrowthExperiment(name="Win-Back Campaign", channel="email", hypothesis="Test"),
            GrowthExperiment(name="Lead Magnet Landing Page", channel="website", hypothesis="Test"),
            GrowthExperiment(name="Onboarding Nurture Sequence", channel="email", hypothesis="Test"),
            GrowthExperiment(name="Live Demo Session", channel="events", hypothesis="Test"),
            GrowthExperiment(name="Customer Feedback Survey", channel="email", hypothesis="Test"),
        ]

        scored = score_experiments_ice(experiments)

        # All should have valid scores
        assert len(scored) == 7
        for exp in scored:
            assert exp.impact >= 1 and exp.impact <= 5
            assert exp.confidence >= 1 and exp.confidence <= 5
            assert exp.effort >= 1 and exp.effort <= 5
            assert exp.priority_score > 0


class TestCopyGeneration:
    """Test copy generation for all channels"""

    def test_copy_generation_email_channel(self):
        """Email channel generates proper email format"""
        business = BusinessProfile(
            business_id="test",
            name="Coffee Shop",
            industry="F&B",
            region="Toronto",
        )
        goal = GrowthGoal(objective="increase sales", horizon_weeks=4)
        experiment = GrowthExperiment(
            name="Test Campaign",
            channel="email",
            hypothesis="This works",
        )
        scored_exp = score_experiments_ice([experiment])[0]

        copy = generate_copy(business, goal, scored_exp)

        # Should have email structure
        assert "Subject:" in copy
        assert business.name in copy
        assert experiment.name in copy
        assert goal.objective in copy

    def test_copy_generation_non_email_channel(self):
        """Non-email channels get appropriate copy"""
        business = BusinessProfile(
            business_id="test",
            name="Store",
            industry="Retail",
            region="NYC",
        )
        goal = GrowthGoal(objective="grow", horizon_weeks=6)
        experiment = GrowthExperiment(
            name="In-Store Promo",
            channel="in-store",
            hypothesis="Works",
        )
        scored_exp = score_experiments_ice([experiment])[0]

        copy = generate_copy(business, goal, scored_exp)

        # Should mention business, experiment, and goal
        assert business.name in copy
        assert experiment.name in copy or "in-store" in copy.lower()
        assert goal.objective in copy


class TestEndToEndPlan:
    """Test complete plan generation"""

    def test_build_complete_growth_plan(self):
        """End-to-end plan generation works"""
        business = BusinessProfile(
            business_id="e2e_test",
            name="Test Coffee Hub",
            industry="Food & Beverage",
            region="Toronto",
        )
        kpis = KpiSnapshot(
            visits=2000,
            leads=350,
            signups=200,
            purchases=80,
            revenue=8400.0,
            retention_rate=0.35,
        )
        goal = GrowthGoal(
            objective="increase repeat purchases",
            horizon_weeks=6,
            constraints="No paid ads",
        )

        plan = build_growth_plan(business, kpis, goal)

        # Verify all components exist
        assert plan.business_profile == business
        assert plan.kpis == kpis
        assert plan.goal == goal
        assert plan.funnel_insight is not None
        assert len(plan.experiments) >= 2
        assert plan.chosen_experiment is not None
        assert plan.copy_suggestion is not None
        assert plan.llm_strategy_commentary is not None

        # Verify chosen is top-ranked
        assert plan.chosen_experiment == plan.experiments[0]

        # Verify priority ordering
        for i in range(len(plan.experiments) - 1):
            assert (
                plan.experiments[i].priority_score
                >= plan.experiments[i + 1].priority_score
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])