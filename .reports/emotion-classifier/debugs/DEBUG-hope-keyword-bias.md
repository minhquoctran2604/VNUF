# Debug Report: Hope Keyword Bias (Disappointment classified as Hope)

## Bug Characterization
| Attribute   | Value          |
| ----------- | -------------- |
| Description | Model predicts "hy_vong" for "Thất vọng quá, mong đợi nhiều mà được cái này huhu" |
| Severity    | Medium         |
| Reproduction | Run `predict_emotion("Thất vọng quá, mong đợi nhiều mà được cái này huhu")` on trained checkpoint |

## Root Cause
**Severe data sparsity of expectation-related keywords during fine-tuning allows pre-training bias to dominate.**
The keyword "mong đợi" only appears 3 times in the entire 10,200 training samples. Because the model is not exposed to enough negative/disappointment contexts using expectation terms during fine-tuning, the pre-trained weights of the transformer (which heavily associate "mong đợi/hy vọng" with positive hope) dominate. The model over-indexes on the "mong đợi" cue and fails to capture the adversative contrast of the phrase "mà được cái này".

## Fix
1. **Data Augmentation:** Add 50-100 synthetic disappointment sentences containing hope-related terms (e.g., "không như mong đợi", "kỳ vọng nhiều rồi lại thất vọng", "hy vọng lắm thất vọng nhiều") to the dataset.
2. **Hyperparameter Optimization:** Increase Weight Decay to `0.05` and decrease Learning Rate to `1e-5` to mitigate overfitting and encourage general semantic alignment rather than keyword memorization.

## Verification
- [ ] Run the keyword analysis script to verify augmented data distribution.
- [ ] Retrain the model and verify if F1-Macro remains stable while `predict_emotion` outputs `that_vong` for the test case.
