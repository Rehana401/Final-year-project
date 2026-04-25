"""
model_training.py — Admin-only Model Training page.

3-step pipeline:
  1. Load & Preprocess dataset
  2. Train all 4 models with cross-validation
  3. Tune best model & save
"""

import streamlit as st
import pandas as pd
import numpy as np
import time

from ml.data_manager import DataManager
from ml.preprocessor import Preprocessor
from ml.model_trainer import ModelTrainer
from ml.model_evaluator import ModelEvaluator


def show_model_training(db):
    """Render the admin model training page."""

    if not st.session_state.get("is_admin"):
        st.error("🔒 This page is restricted to administrators.")
        st.stop()

    st.markdown("## 🧠 Model Training & Evaluation")
    st.markdown("Train, compare, and deploy ML models for fraud detection.")

    # Initialize session state
    if "training_data" not in st.session_state:
        st.session_state["training_data"] = None
    if "trained_models" not in st.session_state:
        st.session_state["trained_models"] = None
    if "metrics_df" not in st.session_state:
        st.session_state["metrics_df"] = None

    # ═══════════════════════════════════════════════════════════════════
    # Step 1: Load & Preprocess Dataset
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("### Step 1: Load & Preprocess Dataset")

    col1, col2 = st.columns([1, 3])
    with col1:
        load_btn = st.button(
            "📥 Load & Preprocess", type="primary",
            use_container_width=True, key="load_dataset_btn",
        )

    if load_btn:
        with st.spinner("Loading and preprocessing dataset... This may take a few minutes."):
            try:
                dm = DataManager()
                df = dm.load_dataset()
                info = dm.get_info()

                st.success(f"✅ Dataset loaded: **{info['rows']:,}** rows, **{info['columns']}** columns")

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Rows", f"{info['rows']:,}")
                col_b.metric("Columns", info['columns'])
                dist = info['label_distribution']
                col_c.metric("Fraud %", f"{dist.get(1, 0) / info['rows'] * 100:.2f}%")

                df_clean = dm.clean()

                preprocessor = Preprocessor()
                data = preprocessor.run_full_pipeline(
                    df_clean, label_col="Is_Fraud",
                    test_size=0.2, apply_smote=True,
                )

                st.session_state["training_data"] = data
                st.success(
                    f"✅ Preprocessing complete!\n\n"
                    f"- Features: {len(data['feature_names'])}\n"
                    f"- Train samples: {len(data['X_train'])}\n"
                    f"- Test samples: {len(data['X_test'])}\n"
                    f"- Scaler saved to `models/scaler.pkl`\n"
                    f"- Feature extractor saved to `models/feature_extractor.pkl`"
                )

            except Exception as e:
                st.error(f"❌ Failed: {e}")
                import traceback
                st.code(traceback.format_exc())

    # Show current status
    if st.session_state["training_data"] is not None:
        data = st.session_state["training_data"]
        st.info(
            f"📦 Dataset ready — "
            f"Train: {len(data['X_train'])} samples, "
            f"Test: {len(data['X_test'])} samples, "
            f"Features: {len(data['feature_names'])}"
        )

    # ═══════════════════════════════════════════════════════════════════
    # Step 2: Train All Models
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### Step 2: Train All Models")

    if st.session_state["training_data"] is None:
        st.warning("⚠️ Load and preprocess the dataset first (Step 1).")
    else:
        col1, col2 = st.columns([1, 3])
        with col1:
            train_btn = st.button(
                "🏋️ Train All Models", type="primary",
                use_container_width=True, key="train_models_btn",
            )

        if train_btn:
            data = st.session_state["training_data"]
            trainer = ModelTrainer()
            evaluator = ModelEvaluator()

            progress_bar = st.progress(0, text="Initializing training...")
            status_text = st.empty()
            model_names = ["LR", "DT", "RF", "XGB"]

            def update_progress(name, text):
                idx = model_names.index(name) if name in model_names else 0
                progress_bar.progress((idx + 1) / len(model_names), text=text)
                status_text.write(text)

            start_time = time.time()
            models = trainer.train_all(
                data["X_train"], data["y_train"],
                k_folds=5, progress_callback=update_progress,
            )
            train_time = time.time() - start_time

            progress_bar.progress(1.0, text="✅ All models trained!")
            st.success(f"✅ Training complete in {train_time:.1f} seconds!")

            # CV results
            st.markdown("#### Cross-Validation Results")
            cv_data = []
            for name, result in trainer.get_cv_results().items():
                cv_data.append({
                    "Model": name,
                    "CV F1 Mean": f"{result['cv_mean']:.4f}",
                    "CV F1 Std": f"±{result['cv_std']:.4f}",
                })
            st.dataframe(pd.DataFrame(cv_data), use_container_width=True, hide_index=True)

            # Test evaluation
            st.markdown("#### Test Set Evaluation")
            metrics_df = evaluator.evaluate_all(models, data["X_test"], data["y_test"])
            st.session_state["metrics_df"] = metrics_df
            st.session_state["trained_models"] = models
            st.session_state["evaluator"] = evaluator
            st.session_state["trainer"] = trainer

            display_df = metrics_df.copy()
            for col in ["Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Best model
            best_name, best_model, best_metrics = evaluator.select_best(models)
            st.success(f"🏆 **Best Model: {best_name}** — F1-Score: {best_metrics['F1-Score']:.4f}")

            # Confusion matrices
            st.markdown("#### Confusion Matrices")
            fig_cm = evaluator.plot_confusion_matrices(models, data["X_test"], data["y_test"])
            st.pyplot(fig_cm)

            # ROC curves
            st.markdown("#### ROC Curves")
            fig_roc = evaluator.plot_roc_curves(models, data["X_test"], data["y_test"])
            st.plotly_chart(fig_roc, use_container_width=True)

            # Feature importance
            st.markdown("#### Feature Importance")
            feature_names = data.get("feature_names", [])
            for name in ["RF", "XGB", "DT"]:
                if name in models and hasattr(models[name], "feature_importances_"):
                    fig_fi = evaluator.plot_feature_importance(
                        models[name], feature_names,
                        title=f"{name} — Feature Importance",
                    )
                    st.plotly_chart(fig_fi, use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════
    # Step 3: Tune & Save Best Model
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### Step 3: Tune & Save Best Model")

    if st.session_state.get("trained_models") is None:
        st.warning("⚠️ Train the models first (Step 2).")
    else:
        evaluator = st.session_state.get("evaluator")
        trainer = st.session_state.get("trainer")
        data = st.session_state["training_data"]

        if evaluator and evaluator.best_model_name:
            best_name = evaluator.best_model_name
            st.info(f"Best model to tune: **{best_name}**")

            col1, col2 = st.columns([1, 3])
            with col1:
                tune_btn = st.button(
                    "🔧 Tune & Save", type="primary",
                    use_container_width=True, key="tune_save_btn",
                )

            if tune_btn:
                with st.spinner(f"Tuning {best_name}... This may take several minutes."):
                    try:
                        tuned_model, best_params, best_score = trainer.tune_best(
                            best_name, data["X_train"], data["y_train"],
                            n_iter=50, k_folds=5
                        )

                        st.success(f"✅ Tuning complete! Best CV F1: {best_score:.4f}")
                        st.json(best_params)

                        # Re-evaluate
                        from sklearn.metrics import (
                            f1_score, accuracy_score, precision_score,
                            recall_score, roc_auc_score,
                        )
                        y_pred = tuned_model.predict(data["X_test"])
                        y_proba = tuned_model.predict_proba(data["X_test"])[:, 1]

                        tuned_metrics = {
                            "Accuracy": accuracy_score(data["y_test"], y_pred),
                            "Precision": precision_score(data["y_test"], y_pred),
                            "Recall": recall_score(data["y_test"], y_pred),
                            "F1-Score": f1_score(data["y_test"], y_pred),
                            "AUC-ROC": roc_auc_score(data["y_test"], y_proba),
                        }

                        st.markdown("#### Tuned Model Metrics")
                        tuned_df = pd.DataFrame([tuned_metrics])
                        for col in tuned_df.columns:
                            tuned_df[col] = tuned_df[col].apply(lambda x: f"{x:.4f}")
                        st.dataframe(tuned_df, use_container_width=True, hide_index=True)

                        # Save
                        model_path = evaluator.save_best_model(tuned_model)
                        st.success(f"💾 Model saved to `{model_path}`")

                        db.save_model_metadata(
                            algorithm_type=best_name,
                            accuracy=tuned_metrics["Accuracy"],
                            precision_score=tuned_metrics["Precision"],
                            recall=tuned_metrics["Recall"],
                            f1_score=tuned_metrics["F1-Score"],
                            auc_roc=tuned_metrics["AUC-ROC"],
                            is_best=True,
                            file_path=model_path,
                        )
                        st.success("📝 Model metadata saved to database.")
                        st.balloons()

                    except Exception as e:
                        st.error(f"❌ Tuning failed: {e}")
                        import traceback
                        st.code(traceback.format_exc())
