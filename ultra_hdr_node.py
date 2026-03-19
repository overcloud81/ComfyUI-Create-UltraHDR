# -*- coding: utf-8 -*-
"""
Create Ultra HDR Image Node for ComfyUI
Version: 1.0.1
Author: overcloud81@github

License: Business Source License 1.1 (BSL-1.1)
Change Date: 2030-01-01
Change License: Apache License 2.0

Description: Converts input sRGB images to Ultra HDR JPEG format using official libultrahdr API-3.
             Compliant with ISO 21496-1, with adaptive non-linear highlight expansion.
             Outputs preview image (with peak brightness overlay) and gain map preview.
描述：将输入的sRGB图像转换为Ultra HDR JPEG格式，使用官方libultrahdr API-3。
     符合ISO 21496-1标准，采用自适应非线性高光扩展。
     输出预览图像（叠加峰值亮度）和增益图预览。

Third-party licenses:
- Google libultrahdr (Apache 2.0): https://github.com/google/libultrahdr
- scipy (BSD 3-Clause): https://scipy.org/
- scikit-image (BSD 3-Clause): https://scikit-image.org/
- Python standard libraries: see Python license.
"""

import os
import locale
import numpy as np
import torch
import folder_paths
import tempfile
import subprocess
from PIL import Image, ImageDraw, ImageFont
import colorsys
import re
import glob
from scipy import ndimage

# 多语言支持 / Multi-language support
def get_system_language():
    try:
        lang_code, _ = locale.getdefaultlocale()
        if lang_code and lang_code.startswith('zh'):
            return 'zh'
    except:
        pass
    return 'en'

CURRENT_LANG = get_system_language()

PARAM_LABELS = {
    'image': {'en': 'Image', 'zh': '图像'},
    'target_luminance': {'en': 'Target Luminance (nits)', 'zh': '目标亮度 (尼特)'},
    'highlight_strength': {'en': 'Highlight Strength', 'zh': '高光强度'},
    'jpeg_quality': {'en': 'JPEG Quality', 'zh': 'JPEG质量'},
    'filename_prefix': {'en': 'Filename Prefix', 'zh': '文件名前缀'},
    'preview_hdr': {'en': 'preview_hdr', 'zh': '预览图像'},
    'gain_preview': {'en': 'gain_preview', 'zh': '增益图预览'},
    'node_name': {'en': 'Create Ultra HDR Image', 'zh': '创建UltraHDR图像并保存'},
}

def tr(key):
    return PARAM_LABELS[key][CURRENT_LANG]

def find_ultrahdr_app():
    if os.name == 'nt':  # Windows
        if subprocess.run(['where', 'ultrahdr_app'], capture_output=True, shell=True).returncode == 0:
            return 'ultrahdr_app'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(base_dir, 'bin', 'windows', 'ultrahdr_app.exe')
        if os.path.exists(app_path):
            return app_path
    elif os.name == 'posix':  # Linux/MacOS
        if subprocess.run(['which', 'ultrahdr_app'], capture_output=True).returncode == 0:
            return 'ultrahdr_app'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(base_dir, 'bin', 'linux', 'ultrahdr_app')):
            return os.path.join(base_dir, 'bin', 'linux', 'ultrahdr_app')
        if os.path.exists(os.path.join(base_dir, 'bin', 'macos', 'ultrahdr_app')):
            return os.path.join(base_dir, 'bin', 'macos', 'ultrahdr_app')
    return None

ULTRAHDR_APP = find_ultrahdr_app()
if ULTRAHDR_APP is None:
    print("Warning: ultrahdr_app not found. Ultra HDR encoding will fail unless you place it in bin/windows/.")
    print("警告：未找到ultrahdr_app，除非将其放入bin/windows/目录，否则Ultra HDR编码将失败。")

def get_large_font(size=24):
    """尝试获取一个较大的字体，如果失败则返回默认字体"""
    try:
        font_paths = [
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        for path in font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

class SDRToUltraHDR:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"display": tr('image')}),
                "target_luminance": ("INT", {"default": 503, "min": 203, "max": 1000, "step": 100}),
                "highlight_strength": ("FLOAT", {"default": 1.0, "min": 0.8, "max": 2.0, "step": 0.1}),
                "jpeg_quality": ("INT", {"default": 95, "min": 50, "max": 100, "step": 1}),
                "filename_prefix": ("STRING", {"default": "UltraHDR"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = (tr('preview_hdr'), tr('gain_preview'))
    FUNCTION = "process"
    CATEGORY = "image/HDR"

    def get_next_filename(self, output_dir, base_prefix, ext=".jpg", padding=5):
        os.makedirs(output_dir, exist_ok=True)
        pattern = os.path.join(output_dir, f"{base_prefix}_*.{ext.lstrip('.')}")
        existing = glob.glob(pattern)
        max_num = 0
        for path in existing:
            basename = os.path.basename(path)
            if basename.startswith(base_prefix + "_") and basename.endswith(ext):
                num_part = basename[len(base_prefix)+1:-len(ext)]
                if num_part.isdigit():
                    max_num = max(max_num, int(num_part))
        next_num = max_num + 1
        filename = f"{base_prefix}_{next_num:0{padding}d}{ext}"
        return os.path.join(output_dir, filename), next_num

    def process(self, image, target_luminance, highlight_strength, jpeg_quality, filename_prefix):
        if image.shape[0] == 0:
            raise ValueError("No image provided")
            
        img_tensor = image[0]
        img_sdr = img_tensor.cpu().numpy().astype(np.float32)

        H, W = img_sdr.shape[0], img_sdr.shape[1]

        # --- 1. sRGB OETF: linearize ---
        linear_sdr = np.where(img_sdr <= 0.04045, 
                             img_sdr / 12.92, 
                             np.power((img_sdr + 0.055) / 1.055, 2.4))

        # --- 2. SDR luminance (Rec.709) ---
        lum_sdr = 0.2126 * linear_sdr[...,0] + 0.7152 * linear_sdr[...,1] + 0.0722 * linear_sdr[...,2]
        print(f"[DEBUG] Original SDR luminance max: {lum_sdr.max():.6f}")

        # ===== Original luminance mapping algorithm =====
        # Developed by overcloud81 – proprietary, adaptive non-linear highlight expansion
        # This algorithm uses dynamic thresholds and local contrast enhancement
        # to preserve dark areas while expanding highlights proportionally to target luminance.
        # =================================================
        sdr_nits = lum_sdr * 100.0
        
        # Local contrast calculation
        local_mean_nits = ndimage.gaussian_filter(sdr_nits, sigma=2.0)
        local_contrast = np.abs(sdr_nits - local_mean_nits) / (local_mean_nits + 1e-6)
        
        # Adaptive thresholds based on target luminance
        scale_factor = target_luminance / 1000.0
        threshold_low = max(min(75.0 * scale_factor, target_luminance * 0.3), 50.0)
        threshold_mid = max(min(85.0 * scale_factor, target_luminance * 0.4), 75.0)
        threshold_high = max(min(95.0 * scale_factor, target_luminance * 0.6), 100.0)
        
        print(f"[DEBUG] Thresholds for target {target_luminance}: low={threshold_low:.1f}, mid={threshold_mid:.1f}, high={threshold_high:.1f}")
        
        hdr_lum_nits = np.copy(sdr_nits)
        
        # Dark region – unchanged
        mask_dark = sdr_nits <= threshold_low
        hdr_lum_nits[mask_dark] = sdr_nits[mask_dark]
        
        # Mid region – gentle power expansion
        mask_mid = (sdr_nits > threshold_low) & (sdr_nits <= threshold_mid)
        if np.any(mask_mid):
            mid_target = min(threshold_low + (target_luminance - threshold_low) * 0.3, target_luminance * 0.4)
            range_mid = threshold_mid - threshold_low
            if range_mid > 0:
                normalized = (sdr_nits[mask_mid] - threshold_low) / range_mid
                expanded = threshold_low + (mid_target - threshold_low) * (normalized ** 1.2)
                hdr_lum_nits[mask_mid] = expanded
        
        # High region – stronger expansion with local contrast
        mask_high = (sdr_nits > threshold_mid) & (sdr_nits <= threshold_high)
        if np.any(mask_high):
            high_start = min(threshold_mid, target_luminance * 0.5)
            high_end = target_luminance * 0.7
            range_high = threshold_high - threshold_mid
            if range_high > 0:
                normalized = (sdr_nits[mask_high] - threshold_mid) / range_high
                expanded = high_start + (high_end - high_start) * (normalized ** 1.5)
                contrast_factor = 1.0 + local_contrast[mask_high] * highlight_strength * 0.5
                hdr_lum_nits[mask_high] = np.minimum(expanded * contrast_factor, target_luminance)
        
        # Very high region – smooth sigmoid approach to target
        mask_very_high = sdr_nits > threshold_high
        if np.any(mask_very_high):
            range_very = 100.0 - threshold_high
            if range_very > 0:
                normalized = (sdr_nits[mask_very_high] - threshold_high) / range_very
                high_base = target_luminance * 0.7
                expanded = high_base + (target_luminance - high_base) * (1.0 - np.exp(-normalized * 2.0))
                contrast_factor = 1.0 + local_contrast[mask_very_high] * highlight_strength * 0.3
                hdr_lum_nits[mask_very_high] = np.clip(expanded * contrast_factor, high_base, target_luminance)

        print(f"[DEBUG] HDR luminance max: {hdr_lum_nits.max():.2f}, target: {target_luminance}")

        # --- 4. Gain map ---
        eps = 1e-8
        gain_map = np.ones_like(lum_sdr)
        gain_map = np.where(sdr_nits > threshold_low,
                            np.clip(hdr_lum_nits / (sdr_nits + eps), 1.0, target_luminance/100.0),
                            1.0)
        gain_map = np.where(gain_map > 1.0,
                           1.0 + (gain_map - 1.0) * highlight_strength,
                           gain_map)
        max_possible_gain = target_luminance / 100.0
        gain_map = np.clip(gain_map, 1.0, min(8.0, max_possible_gain))

        # --- 5. HDR RGB reconstruction with chromaticity preservation ---
        chroma_r = linear_sdr[..., 0] / (lum_sdr + eps)
        chroma_g = linear_sdr[..., 1] / (lum_sdr + eps)
        chroma_b = linear_sdr[..., 2] / (lum_sdr + eps)
        
        hdr_lum_linear = hdr_lum_nits / 100.0
        
        # Saturation adjustment for bright areas
        sat_factor = np.ones_like(hdr_lum_linear)
        high_lum_mask = hdr_lum_linear > 1.0
        if np.any(high_lum_mask):
            excess = np.clip(hdr_lum_linear[high_lum_mask] - 1.0, 0.0, 10.0)
            sat_factor[high_lum_mask] = np.exp(-excess * 0.2)
        
        adjusted_chroma_r = chroma_r * sat_factor
        adjusted_chroma_g = chroma_g * sat_factor
        adjusted_chroma_b = chroma_b * sat_factor
        
        total_chroma = adjusted_chroma_r + adjusted_chroma_g + adjusted_chroma_b
        total_chroma = np.where(total_chroma == 0, 1.0, total_chroma)
        norm = lum_sdr / (total_chroma + eps)
        
        hdr_rgb = np.stack([
            adjusted_chroma_r * norm * hdr_lum_linear,
            adjusted_chroma_g * norm * hdr_lum_linear,
            adjusted_chroma_b * norm * hdr_lum_linear
        ], axis=-1)
        
        max_hdr_value = target_luminance / 100.0
        hdr_rgb = np.clip(hdr_rgb, 0.0, max_hdr_value)
        print(f"[DEBUG] Final HDR RGB max: {hdr_rgb.max():.6f}, target limit: {max_hdr_value:.6f}")

        # --- 6. Gain info ---
        actual_gain_min = gain_map.min()
        actual_gain_max = gain_map.max()
        print(f"[DEBUG] Gain map range: {actual_gain_min:.3f} to {actual_gain_max:.3f}")

        # --- 7. SDR base unchanged ---
        sdr_base = img_sdr

        # --- 8. Output path ---
        norm_prefix = filename_prefix.replace('\\', '/')
        if '/' in norm_prefix:
            subfolder_path = os.path.dirname(norm_prefix)
            base_prefix = os.path.basename(norm_prefix)
            full_output_folder = os.path.join(folder_paths.get_output_directory(), subfolder_path)
        else:
            base_prefix = filename_prefix
            full_output_folder = folder_paths.get_output_directory()
        output_path, counter = self.get_next_filename(full_output_folder, base_prefix, ".jpg", padding=5)

        # --- 9. Encode with ultrahdr_app ---
        if ULTRAHDR_APP is None:
            raise RuntimeError("ultrahdr_app not found. Please place ultrahdr_app in appropriate bin directory.")
        
        try:
            self.encode_ultrahdr_api3(sdr_base, hdr_rgb, target_luminance, jpeg_quality,
                                       output_path, W, H, actual_gain_min, actual_gain_max)
        except Exception as e:
            print(f"Error during Ultra HDR encoding: {str(e)}")
            raise

        # --- 10. Preview image with peak brightness ---
        peak_luminance = int(np.max(hdr_lum_nits))
        preview_img = (np.clip(sdr_base, 0, 1) * 255).astype(np.uint8)
        preview_pil = Image.fromarray(preview_img)
        draw = ImageDraw.Draw(preview_pil)
        text = f"Peak: {peak_luminance} nits"
        font = get_large_font(24)
        draw.text((12, 12), text, fill=(0, 0, 0, 200), font=font)
        draw.text((10, 10), text, fill=(255, 255, 255), font=font)
        preview_tensor = torch.from_numpy(np.array(preview_pil).astype(np.float32) / 255.0).unsqueeze(0)

        # --- 11. Gain map preview ---
        gain_norm = (gain_map - 1.0) / 7.0
        gain_gray = np.stack([gain_norm] * 3, axis=-1).astype(np.float32)
        gain_preview_tensor = torch.from_numpy(gain_gray).unsqueeze(0)

        return (preview_tensor, gain_preview_tensor)

    def encode_ultrahdr_api3(self, sdr_image, linear_hdr, target_luminance, quality,
                              output_path, width, height, gain_min, gain_max):
        sdr_temp = None
        hdr_temp = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as sdr_file:
                sdr_img = Image.fromarray((np.clip(sdr_image, 0, 1) * 255).astype(np.uint8))
                sdr_img.save(sdr_file.name, format='JPEG', quality=quality, optimize=True)
                sdr_temp = sdr_file.name

            # RGB -> YUV Rec.709
            r, g, b = linear_hdr[..., 0], linear_hdr[..., 1], linear_hdr[..., 2]
            kr, kg, kb = 0.2126, 0.7152, 0.0722
            y = kr * r + kg * g + kb * b

            norm_r = np.clip(r / target_luminance, 0, 1)
            norm_g = np.clip(g / target_luminance, 0, 1)
            norm_b = np.clip(b / target_luminance, 0, 1)

            u = 0.5 - 0.1146 * norm_r - 0.3854 * norm_g + 0.5 * norm_b
            v = 0.5 + 0.5 * norm_r - 0.4542 * norm_g - 0.0458 * norm_b

            def downsample(plane):
                h, w = plane.shape
                if h % 2: plane = np.pad(plane, ((0,1),(0,0)), mode='edge')
                if w % 2: plane = np.pad(plane, ((0,0),(0,1)), mode='edge')
                h2, w2 = h//2, w//2
                return plane[:h2*2, :w2*2].reshape(h2,2,w2,2).mean(axis=(1,3))

            u_d = downsample(u)
            v_d = downsample(v)

            y_q = np.round(y * (940-64) + 64).clip(64,940).astype(np.uint16)
            u_q = np.round(u_d * (940-64) + 64).clip(64,940).astype(np.uint16)
            v_q = np.round(v_d * (940-64) + 64).clip(64,940).astype(np.uint16)

            with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as hdr_file:
                y_plane = y_q.view(y_q.dtype.newbyteorder('>'))
                hdr_file.write(y_plane.tobytes())
                u_flat = u_q.flatten()
                v_flat = v_q.flatten()
                uv = np.empty((u_flat.size + v_flat.size,), dtype=np.uint16)
                uv[0::2] = u_flat.view(u_flat.dtype.newbyteorder('>'))
                uv[1::2] = v_flat.view(v_flat.dtype.newbyteorder('>'))
                hdr_file.write(uv.tobytes())
                hdr_temp = hdr_file.name

            cmd = [
                ULTRAHDR_APP,
                '-m', '0',
                '-i', sdr_temp,
                '-p', hdr_temp,
                '-a', '0',
                '-c', '0',
                '-C', '0',
                '-t', '2',
                '-L', str(target_luminance),
                '-w', str(width),
                '-h', str(height),
                '-s', '1',
                '-z', output_path,
                '-q', str(quality),
                '-Q', '100',
                '-M', '0',
                '-k', f'{gain_min:.6f}',
                '-K', f'{gain_max:.6f}',
            ]

            print(f"[DEBUG] Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Ultra HDR encoding failed: {result.stderr}")
            else:
                print("[SUCCESS] Ultra HDR encoding completed successfully")

        finally:
            if sdr_temp and os.path.exists(sdr_temp):
                os.unlink(sdr_temp)
            if hdr_temp and os.path.exists(hdr_temp):
                os.unlink(hdr_temp)

NODE_CLASS_MAPPINGS = {
    "SDRToUltraHDR": SDRToUltraHDR,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SDRToUltraHDR": tr('node_name'),
}
