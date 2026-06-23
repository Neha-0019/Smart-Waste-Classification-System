"""
waste_detector.py — Waste Detection and Classification

WasteDetector class providing model loading, inference, and Grad-CAM
visualization for multi-label waste classification using EfficientNet-B3.

Toggle USE_MOCK_MODEL to switch between mock inference and real model.
"""

import numpy as np
from PIL import Image
import cv2

from taxonomy import WASTE_CLASSES

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG — Set to False when a real fine-tuned checkpoint
#          is available at MODEL_CHECKPOINT_PATH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE_MOCK_MODEL = True
MODEL_CHECKPOINT_PATH = "models/waste_efficientnet_b3.pth"
CONFIDENCE_THRESHOLD = 0.25
INPUT_SIZE = 300
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class WasteDetector:
    """
    Unified waste detection interface.

    Provides predict() for multi-label classification and get_gradcam()
    for class activation heatmap overlays. Automatically falls back to
    mock inference when USE_MOCK_MODEL is True or no checkpoint exists.
    """

    def __init__(self):
        """Initialize the detector, loading model weights if available."""
        self.classes = WASTE_CLASSES
        self.num_classes = len(self.classes)
        self.model = None
        self.device = None

        if not USE_MOCK_MODEL:
            self._load_real_model()

    def _load_real_model(self):
        """Load the fine-tuned EfficientNet-B3 model from checkpoint."""
        try:
            import torch
            from efficientnet_pytorch import EfficientNet

            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )

            # Load EfficientNet-B3 and modify the classifier head
            self.model = EfficientNet.from_pretrained("efficientnet-b3")
            in_features = self.model._fc.in_features
            self.model._fc = torch.nn.Linear(in_features, self.num_classes)

            # Load fine-tuned weights
            checkpoint = torch.load(
                MODEL_CHECKPOINT_PATH, map_location=self.device
            )
            self.model.load_state_dict(checkpoint)
            self.model.to(self.device)
            self.model.eval()

        except (FileNotFoundError, RuntimeError) as e:
            print(f"[WasteDetector] Could not load model: {e}")
            print("[WasteDetector] Falling back to mock inference.")
            self.model = None

    def _preprocess(self, image_pil: Image.Image) -> np.ndarray:
        """Resize and normalize a PIL image for model input."""
        img = image_pil.convert("RGB").resize(
            (INPUT_SIZE, INPUT_SIZE), Image.LANCZOS
        )
        arr = np.array(img, dtype=np.float32) / 255.0
        # Normalize with ImageNet stats
        arr = (arr - IMAGENET_MEAN) / IMAGENET_STD
        return arr

    def _mock_predict(self, image_pil: Image.Image) -> dict:
        """
        Generate plausible multi-label predictions using image
        colour statistics. Produces deterministic but varied output.
        """
        img = image_pil.convert("RGB").resize((INPUT_SIZE, INPUT_SIZE))
        arr = np.array(img, dtype=np.float32) / 255.0

        # Extract colour channel statistics
        r_mean, g_mean, b_mean = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
        brightness = arr.mean()
        r_std, g_std, b_std = arr[:, :, 0].std(), arr[:, :, 1].std(), arr[:, :, 2].std()
        saturation = max(r_std, g_std, b_std)

        # Build per-class affinities based on colour heuristics
        affinities = np.zeros(self.num_classes, dtype=np.float32)

        # Biodegradable — green/brown tones, natural colours
        affinities[0] = 0.3 + 0.5 * g_mean - 0.2 * b_mean + 0.1 * (1 - saturation)

        # Plastic — high saturation, blue-ish tones common
        affinities[1] = 0.2 + 0.4 * b_mean + 0.3 * saturation

        # Metal — low saturation, grey tones, high brightness variation
        affinities[2] = 0.2 + 0.5 * (1 - saturation) + 0.2 * brightness

        # Glass — high brightness, low saturation, transparent feel
        affinities[3] = 0.15 + 0.4 * brightness + 0.3 * (1 - saturation)

        # E-Waste — dark, mixed colours, moderate saturation
        affinities[4] = 0.15 + 0.3 * (1 - brightness) + 0.2 * saturation

        # Pharmaceutical — white/pastel, clean look
        affinities[5] = 0.1 + 0.4 * brightness + 0.2 * (1 - saturation) - 0.1 * g_mean

        # Hazardous — red/yellow warning tones
        affinities[6] = 0.1 + 0.4 * r_mean + 0.2 * (r_mean - b_mean)

        # Textile — varied colours, moderate brightness
        affinities[7] = 0.15 + 0.3 * saturation + 0.2 * (1 - abs(brightness - 0.5))

        # Construction Debris — brown/grey, low saturation
        affinities[8] = 0.15 + 0.3 * r_mean * (1 - saturation) + 0.2 * (1 - brightness)

        # Apply sigmoid-like transformation and add controlled noise
        np.random.seed(int(r_mean * 1000) % 2**31)
        noise = np.random.normal(0, 0.05, self.num_classes).astype(np.float32)
        raw_scores = 1.0 / (1.0 + np.exp(-(affinities + noise - 0.3) * 5))

        # Ensure at least one class is prominent
        raw_scores[np.argmax(affinities)] = max(
            raw_scores[np.argmax(affinities)], 0.65
        )

        # Build result dict
        predictions = {}
        for i, class_name in enumerate(self.classes):
            predictions[class_name] = float(np.clip(raw_scores[i], 0.01, 0.99))

        return predictions

    def _real_predict(self, image_pil: Image.Image) -> dict:
        """Run inference through the real EfficientNet-B3 model."""
        import torch

        arr = self._preprocess(image_pil)
        # HWC → CHW, add batch dimension
        tensor = torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0).float()
        tensor = tensor.to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.sigmoid(logits).squeeze().cpu().numpy()

        predictions = {}
        for i, class_name in enumerate(self.classes):
            predictions[class_name] = float(probs[i])

        return predictions

    def predict(self, image_pil: Image.Image) -> dict:
        """
        Classify waste in the given image.

        Args:
            image_pil: PIL Image to classify.

        Returns:
            Dict mapping class names to confidence scores (0–1).
        """
        if USE_MOCK_MODEL or self.model is None:
            return self._mock_predict(image_pil)
        return self._real_predict(image_pil)

    def _mock_gradcam(
        self, image_pil: Image.Image, target_class: str
    ) -> np.ndarray:
        """
        Generate a synthetic Grad-CAM heatmap overlay.

        Uses a gaussian blob positioned based on image content and the
        target class index, producing a visually plausible attention map.
        """
        img = image_pil.convert("RGB").resize((INPUT_SIZE, INPUT_SIZE))
        img_arr = np.array(img, dtype=np.float32)

        # Create a gaussian heatmap — position varies by class index
        class_idx = self.classes.index(target_class) if target_class in self.classes else 0
        np.random.seed(class_idx * 42 + int(img_arr.mean()))

        # Generate 2–3 gaussian blobs for more realistic attention
        heatmap = np.zeros((INPUT_SIZE, INPUT_SIZE), dtype=np.float32)
        num_blobs = np.random.randint(2, 4)

        for _ in range(num_blobs):
            cy = np.random.randint(INPUT_SIZE // 4, 3 * INPUT_SIZE // 4)
            cx = np.random.randint(INPUT_SIZE // 4, 3 * INPUT_SIZE // 4)
            sigma = np.random.randint(30, 80)
            y_grid, x_grid = np.mgrid[0:INPUT_SIZE, 0:INPUT_SIZE]
            blob = np.exp(
                -((x_grid - cx) ** 2 + (y_grid - cy) ** 2) / (2 * sigma**2)
            )
            heatmap += blob

        # Normalize to 0–1
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

        # Apply jet colormap
        heatmap_colored = cv2.applyColorMap(
            (heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        # Overlay at 50% opacity
        overlay = (0.5 * img_arr + 0.5 * heatmap_colored.astype(np.float32)).astype(
            np.uint8
        )
        return overlay

    def _real_gradcam(
        self, image_pil: Image.Image, target_class: str
    ) -> np.ndarray:
        """Generate Grad-CAM heatmap using pytorch-grad-cam on the real model."""
        import torch
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.image import show_cam_on_image

        arr = self._preprocess(image_pil)
        tensor = torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0).float()
        tensor = tensor.to(self.device)

        # Target the last convolutional layer of EfficientNet-B3
        target_layer = self.model._conv_head

        class_idx = self.classes.index(target_class)

        class ClassTarget:
            def __init__(self, category):
                self.category = category

            def __call__(self, model_output):
                return model_output[:, self.category]

        cam = GradCAM(model=self.model, target_layers=[target_layer])
        targets = [ClassTarget(class_idx)]

        grayscale_cam = cam(input_tensor=tensor, targets=targets)
        grayscale_cam = grayscale_cam[0, :]

        # Prepare RGB image normalised to 0–1
        img_resized = image_pil.convert("RGB").resize((INPUT_SIZE, INPUT_SIZE))
        rgb_img = np.array(img_resized, dtype=np.float32) / 255.0

        # Create overlay with 50% opacity
        overlay = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True, image_weight=0.5)
        return overlay

    def get_gradcam(
        self, image_pil: Image.Image, target_class: str
    ) -> np.ndarray:
        """
        Generate Grad-CAM class activation heatmap overlay.

        Args:
            image_pil: PIL Image to visualise.
            target_class: Which waste class to generate the heatmap for.

        Returns:
            numpy array (H, W, 3) of the overlay image in RGB.
        """
        if USE_MOCK_MODEL or self.model is None:
            return self._mock_gradcam(image_pil, target_class)
        return self._real_gradcam(image_pil, target_class)

    @staticmethod
    def filter_predictions(
        predictions: dict, threshold: float = CONFIDENCE_THRESHOLD
    ) -> dict:
        """
        Filter predictions above confidence threshold.

        Always returns at least one class (highest scoring) even if
        all scores fall below the threshold.
        """
        filtered = {k: v for k, v in predictions.items() if v >= threshold}

        if not filtered:
            top_class = max(predictions, key=predictions.get)
            filtered = {top_class: predictions[top_class]}

        return dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def normalize_to_percentages(filtered_predictions: dict) -> dict:
        """
        Normalize filtered confidence scores to sum to 100%.

        Returns dict mapping class names to percentage values.
        """
        total = sum(filtered_predictions.values())
        if total == 0:
            total = 1.0

        return {
            k: round((v / total) * 100, 1)
            for k, v in filtered_predictions.items()
        }
