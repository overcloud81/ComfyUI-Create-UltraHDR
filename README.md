# ComfyUI Create Ultra HDR Image

**English** | **中文**

### 📖 Description / 描述

**English:** This custom node for ComfyUI converts input sRGB images to **Ultra HDR JPEG format (ISO 21496-1)** using Google's official libultrahdr library. It provides professional color management, accurate luminance mapping, and a grayscale gain map to ensure perfect color reproduction.  
Dark regions (≤75% SDR) are kept at original brightness; highlights are expanded with adaptive non‑linear mapping.  
The node also outputs a preview of the gain map (grayscale) for debugging.

**中文：** 本ComfyUI自定义节点使用Google官方libultrahdr库，将输入的sRGB图像转换为**Ultra HDR JPEG格式（ISO 21496-1）**。它集成了专业色彩管理、精确的亮度映射和灰度增益图，确保色彩完美还原。  
暗部（≤75% SDR）保持原亮度；高光采用自适应非线性映射进行扩展。  
节点额外输出增益图预览（灰度图），便于调试。

### ✨ Key Features / 核心特性

**English:**
- **Single‑channel grayscale gain map** – Strictly follows the Ultra HDR standard, avoids color shifts common in multi‑channel gain maps.
- **Proprietary luminance mapping algorithm** – Developed by the author, uses dynamic thresholds and local contrast enhancement to preserve dark areas while expanding highlights.
- **Automatic file numbering** – Never overwrites existing files; supports subfolders in the filename prefix (e.g., `HDR/test/UltraHDR`).
- **Preview overlay with peak brightness** – The first output is a preview image with a “Peak: XXX nits” text overlay (large font) for easy verification.
- **Gain map preview** – The second output is a grayscale visualization of the gain map (values normalized to 0–1), which can be connected to a `PreviewImage` node for debugging.
- **Bilingual UI** – Node parameters automatically switch between Chinese and English based on your system language.
- **No extra downloads** – All dependencies (including `ultrahdr_app`) are bundled – just drop and use.

**中文：**
- **单通道灰度增益图** – 严格遵循Ultra HDR标准，避免多通道增益图常见的偏色问题。
- **自有亮度映射算法** – 由作者原创设计，使用动态阈值和局部对比度增强，在保护暗部的同时精准扩展高光。
- **手动文件编号** – 自动递增文件名，避免覆盖；支持文件名前缀中的子文件夹（例如 `HDR/test/UltraHDR`）。
- **预览图像叠加峰值亮度** – 第一输出为带有“Peak: XXX nits”文本的预览图像（大字号），便于调试。
- **增益图预览** – 第二输出为增益图的灰度可视化（数值归一化到0-1），可连接 `PreviewImage` 节点查看，用于调试。
- **双语界面** – 节点参数根据系统语言自动切换中文/英文。
- **开箱即用** – 所有依赖（包括 `ultrahdr_app` 可执行文件）均已打包，无需额外下载。

### 🏆 Uniqueness & Advantages / 独家性与前瞻性优势

**English:** To the best of our knowledge, **no other node in the ComfyUI ecosystem can output Ultra HDR JPEG images**. More importantly, **even the most advanced closed‑source large models (both international and domestic) cannot directly output images in the Ultra HDR JPEG format (ISO 21496-1)**. According to their official documentation and API specifications:

International models:
- OpenAI GPT-4o / DALL·E 3 – outputs standard JPEG/PNG, cannot output Ultra HDR.
- Anthropic Claude 3.5 Sonnet – supports only standard image formats, cannot output Ultra HDR.
- Google Gemini 2.0 – processes standard image formats, generates standard PNG, cannot output Ultra HDR.
- Midjourney V7 – generates standard PNG with sRGB color space, cannot output Ultra HDR.
- Stable Diffusion 3.5 – outputs standard PNG/JPEG, cannot output Ultra HDR.

Domestic models:
- 百度文心一言 (ERNIE Bot) – image generation outputs standard JPEG/PNG, cannot output Ultra HDR.
- 阿里通义千问 (Tongyi Qianwen) – supports image recognition but not HDR generation, cannot output Ultra HDR.
- 智谱清言 (ChatGLM) – image output in standard formats only, cannot output Ultra HDR.
- 腾讯混元 (Hunyuan) – generates standard images without HDR metadata, cannot output Ultra HDR.
- 月之暗面 Kimi – does not support image generation, cannot output Ultra HDR.
- 字节跳动豆包 (Doubao) – image output in standard formats, cannot output Ultra HDR.

While these models can generate high-quality standard images, they lack the ability to embed gain maps and HDR metadata required for true Ultra HDR compatibility. Our node fills this gap by providing a professional-grade solution for creating Ultra HDR images within the ComfyUI ecosystem.

**中文：** 据我们所知，**目前ComfyUI生态中尚无其他节点能够输出Ultra HDR JPEG图像**。更重要的是，**即便是最先进的闭源大模型（包括国内外主流模型）也无法直接输出Ultra HDR JPEG格式（ISO 21496-1）的图像**。根据官方文档和API说明：

国际模型：
- OpenAI GPT-4o / DALL·E 3 – 输出标准JPEG/PNG，无法输出Ultra HDR。
- Anthropic Claude 3.5 Sonnet – 仅支持标准图像格式，无法输出Ultra HDR。
- Google Gemini 2.0 – 处理标准图像格式，生成标准PNG，无法输出Ultra HDR。
- Midjourney V7 – 生成标准PNG，sRGB色彩空间，无法输出Ultra HDR。
- Stable Diffusion 3.5 – 输出标准PNG/JPEG，无法输出Ultra HDR。

国内模型：
- 百度文心一言 – 图像生成输出标准JPEG/PNG，无法输出Ultra HDR。
- 阿里通义千问 – 支持图像识别，不生成HDR格式，无法输出Ultra HDR。
- 智谱清言 – 图像输出仅为标准格式，无法输出Ultra HDR。
- 腾讯混元 – 生成标准图像，无HDR元数据，无法输出Ultra HDR。
- 月之暗面 Kimi – 不支持图像生成，无法输出Ultra HDR。
- 字节跳动豆包 – 图像输出为标准格式，无法输出Ultra HDR。

这些模型可以生成高质量的标准图像，但均缺乏嵌入增益图和HDR元数据的能力，无法实现真正的Ultra HDR兼容性。本节点填补了这一空白，为ComfyUI生态提供了专业的Ultra HDR图像创建方案。

### 📸 Understanding Ultra HDR Technology / 了解Ultra HDR技术

#### What is Ultra HDR? / 什么是Ultra HDR？

**English:** Ultra HDR is a next-generation image format introduced by Google with Android 14 that revolutionizes mobile photography by enabling true 10-bit HDR capture. Unlike traditional HDR techniques that simulate effects through image stacking, Ultra HDR captures a single frame while preserving expanded dynamic range.

The core innovation is its clever use of the universally compatible JPEG format. An Ultra HDR image consists of:
- A standard 8‑bit JPEG base image (SDR version) – viewable on all devices.
- A gain map – lower‑resolution single‑channel or multi‑channel image containing brightness adjustment metadata.
- ISO 21496‑1 standardized metadata – defining how to reconstruct the HDR version.

This structure ensures **perfect backward compatibility**: devices and apps without HDR support simply display the SDR JPEG, while HDR‑capable systems apply the gain map to reconstruct the full 10‑bit HDR image with extended colors and contrast. The SDR base image remains completely untouched and visible on any device, making Ultra HDR a drop‑in replacement for ordinary JPEGs with no compatibility risk.

**中文：** Ultra HDR 是 Google 在 Android 14 中推出的下一代图像格式，通过真正的 10-bit HDR 捕获革新了移动摄影。与传统的通过图像堆叠模拟效果的 HDR 技术不同，Ultra HDR 在保留扩展动态范围的同时捕获单帧图像。

其核心创新在于巧妙利用了普遍兼容的 JPEG 格式。一张 Ultra HDR 图像包含：
- 一个标准的 8-bit JPEG 基底图像（SDR 版本） – 在所有设备上均可查看。
- 一个增益图 – 较低分辨率的单通道或多通道图像，包含亮度调整元数据。
- ISO 21496-1 标准化元数据 – 定义如何重建 HDR 版本。

这种结构确保了**完美的向后兼容性**：不支持 HDR 的设备和应用仅显示 SDR JPEG，而支持 HDR 的系统则应用增益图重建具有扩展色彩和对比度的完整 10-bit HDR 图像。SDR 基底图像完全保持不变，可在任何设备上查看，使得 Ultra HDR 成为普通 JPEG 的即插即用替代品，没有任何兼容性风险。

#### How the Gain Map Works / 增益图的工作原理

**English:** The gain map is the heart of Ultra HDR technology. It functions as a per‑pixel brightness multiplier that transforms the SDR base into the HDR image:

HDR(x,y,c) = SDR(x,y,c) × gain(x,y)

In engineering terms, the gain map stores linear‑domain multiplicative compensation information derived from the ratio between HDR linear luminance and SDR linear luminance. When applied, it recovers highlight and shadow details that would otherwise be lost in a standard 8‑bit JPEG.

Why this matters:
- No tone‑mapping loss – Unlike simple dynamic range compression, the gain map preserves the original scene's luminance relationships.
- Precise control – The gain map can be single‑channel (luminance only) or multi‑channel (per‑color), offering flexibility in color reproduction.

Our node's single‑channel grayscale gain map strictly follows this standard, avoiding the color shifts that can occur with multi‑channel implementations.

**中文：** 增益图是 Ultra HDR 技术的核心。它充当逐像素亮度乘数，将 SDR 基底转换为 HDR 图像：

HDR(x,y,c) = SDR(x,y,c) × gain(x,y)

在工程术语中，增益图存储了从 HDR 线性亮度与 SDR 线性亮度之比导出的线性域乘法补偿信息。应用时，它恢复了在标准 8-bit JPEG 中会丢失的高光和阴影细节。

其重要性体现在：
- 无色调映射损失 – 与简单的动态范围压缩不同，增益图保留了原始场景的亮度关系。
- 精确控制 – 增益图可以是单通道（仅亮度）或多通道（每颜色），在色彩再现方面提供了灵活性。

本节点的单通道灰度增益图严格遵循此标准，避免了多通道实现中可能出现的色偏。

#### Full Cross‑Platform Compatibility / 完整的跨平台兼容性

**English:** The ISO 21496‑1 standard has unified HDR across ecosystems:

- Android: Native support from Android 14 (API level 34) for Ultra HDR images.
- iOS: Native support from iOS 18, iPadOS 18, macOS 15 for ISO 21496‑1 gain maps.
- Windows: Windows 11 includes native support via the HEIF Image Extension.
- Web: Chrome, Edge, and other Chromium‑based browsers support Ultra HDR rendering.
- Google Photos: Full support for uploading, viewing, and sharing Ultra HDR images.
- Adobe Lightroom: Exports Ultra HDR images with proper gain map embedding.

This means images created with this node will display correctly on billions of devices worldwide, from the latest smartphones to desktop browsers, without any additional plugins or conversions. On non‑HDR devices, they appear as standard JPEGs with no visible difference.

**中文：** ISO 21496-1 标准统一了各生态系统的 HDR：

- Android：从 Android 14（API 级别 34）开始原生支持 Ultra HDR 图像。
- iOS：从 iOS 18、iPadOS 18、macOS 15 开始原生支持 ISO 21496-1 增益图。
- Windows：Windows 11 通过 HEIF 图像扩展包含原生支持。
- Web：Chrome、Edge 及其他基于 Chromium 的浏览器支持 Ultra HDR 渲染。
- Google Photos：完全支持上传、查看和分享 Ultra HDR 图像。
- Adobe Lightroom：导出带有正确增益图嵌入的 Ultra HDR 图像。

这意味着使用本节点创建的图像将在全球数十亿设备上正确显示，从最新智能手机到桌面浏览器，无需任何额外插件或转换。在非 HDR 设备上，它们作为标准 JPEG 显示，肉眼观察无任何差异。

### 📱 Social Media Support / 社交平台支持

**English:**  
- **小红书 (RedNote)** and **酷安 (CoolAPK)** have been confirmed to support uploading and displaying Ultra HDR images. Users have successfully shared HDR photos with HDR metadata preserved.  
- For international platforms like Instagram, Twitter/X, and Facebook, official support is not yet announced, but is expected as the ISO 21496-1 standard becomes more widespread.

**中文：**  
- **小红书** 和 **酷安** 已被确认支持上传和显示 Ultra HDR 图像。用户已成功分享带有HDR元数据的照片。  
- 对于 Instagram、Twitter/X、Facebook 等国际平台，目前尚未有官方支持公告，但随着 ISO 21496-1 标准的普及，预计未来将会支持。

### 📦 Installation / 安装

**English:**
1. Clone or download this repository into your `ComfyUI/custom_nodes/` folder:

    cd ComfyUI/custom_nodes
    git clone https://github.com/overcloud81/ComfyUI-Create-UltraHDR.git

2. Install required Python dependency:

    pip install scipy

3. Restart ComfyUI. The node will appear in the `image/HDR` category with the name **“Create Ultra HDR Image”** (English) or **“创建UltraHDR图像并保存”** (Chinese).

**中文：**
1. 将本仓库克隆或下载到 `ComfyUI/custom_nodes/` 目录下：

    cd ComfyUI/custom_nodes
    git clone https://github.com/overcloud81/ComfyUI-Create-UltraHDR.git

2. 安装所需的 Python 依赖：

    pip install scipy

3. 重启ComfyUI，节点将出现在“image/HDR”分类中，名称为**“创建UltraHDR图像并保存”**（中文）或**“Create Ultra HDR Image”**（英文）。

### 🔧 Usage / 使用说明

**English:**
1. Connect an sRGB image (`IMAGE` type) to the node’s `image` input.
2. Adjust the parameters:
   - **Target Luminance** – Peak HDR brightness in nits (203–1000, default 503). Must be at least 203 nits per Ultra HDR spec.
   - **Highlight Strength** – Controls the intensity of highlight expansion (0.8–2.0, default 1.0). Higher values produce more dramatic highlights.
   - **JPEG Quality** – Compression quality for the SDR base JPEG (50–100, default 95).
   - **Filename Prefix** – Output filename prefix; can include a subfolder (e.g., `HDR/test/UltraHDR`).
3. Execute the workflow. The node outputs:
   - **First output (`preview_hdr`)**: a preview image with a “Peak: XXX nits” overlay. Connect a `PreviewImage` node to view it.
   - **Second output (`gain_preview`)**: a grayscale visualization of the gain map (values normalized to 0–1). Connect another `PreviewImage` node to debug the gain map.
4. The Ultra HDR JPEG file is saved in the output folder with an automatically incremented name (`prefix_00001.jpg`, `prefix_00002.jpg`, …).

**中文：**
1. 连接任意sRGB图像（`IMAGE`类型）到节点的`image`输入端口。
2. 设置参数：
   - **目标亮度** – HDR峰值亮度，范围203~1000尼特，默认503。根据Ultra HDR规范，最小值必须为203尼特。
   - **高光强度** – 控制高光扩展的强度（0.8–2.0，默认1.0）。值越大高光效果越强。
   - **JPEG质量** – SDR基底JPEG的压缩质量，范围50~100，默认95。
   - **文件名前缀** – 输出文件的前缀，可包含子文件夹（例如 `HDR/test/UltraHDR`）。
3. 运行工作流，节点输出：
   - **第一输出 (`preview_hdr`)**：带有“Peak: XXX nits”文本的预览图像。连接 `PreviewImage` 节点查看。
   - **第二输出 (`gain_preview`)**：增益图的灰度可视化（数值归一化到0-1）。连接另一个 `PreviewImage` 节点调试增益图。
4. Ultra HDR JPEG文件将在输出目录中自动递增命名保存（例如 `前缀_00001.jpg`、`前缀_00002.jpg`）。

### 📜 License & Commercial Use / 开源协议与商业授权

**English:** This project is licensed under the **Business Source License 1.1 (BSL-1.1)** (Copyright 2026 overcloud81). You may freely use, modify, and distribute it for personal and non‑commercial purposes.

**If you wish to integrate this node (including its code, algorithms, or bundled executables) into any commercial product or service, or to distribute it in a closed‑source context, you must obtain a commercial license from the author.**

The BSL-1.1 includes a Change Date (2030-01-01), after which the code will automatically convert to Apache License 2.0.

For commercial licensing inquiries, please contact: `35592401@qq.com`. You may also contact me via GitHub.com or ModelScope.cn (username: `overcloud81`) for licensing inquiries.

The full text of the Business Source License is available in the `LICENSE` file.

**中文：** 本项目采用 **Business Source License 1.1 (BSL-1.1)** 许可证（版权所有 2026 overcloud81）。个人和非商业用途可以免费使用、修改和分发。

**如需将本项目（包括其代码、算法或编译后的可执行文件）集成到任何商业产品或服务中，或用于闭源分发，必须获得作者的商业授权。**

BSL-1.1 包含一个转换日期（2030-01-01），届时代码将自动转为 Apache 2.0 许可证。

商业授权请联系：`35592401@qq.com`。也可通过 GitHub.com 或 ModelScope.cn（用户名：`overcloud81`）留言联系。

BSL 许可证的完整副本见项目根目录下的 `LICENSE` 文件。

### 🙏 Acknowledgements / 鸣谢

**English:**
- Google libultrahdr (Apache 2.0): https://github.com/google/libultrahdr
- scipy (BSD 3-Clause): https://scipy.org/ – used for Gaussian filtering in local contrast calculation.
- scikit-image (BSD 3-Clause): https://scikit-image.org/ – (optional) used for gain map downsampling.
- Python standard libraries: os, locale, numpy, torch, PIL, colorsys, re, glob, tempfile, subprocess

**中文：**
- Google libultrahdr (Apache 2.0)：https://github.com/google/libultrahdr
- scipy (BSD 3-Clause)：https://scipy.org/ – 用于局部对比度计算中的高斯滤波。
- scikit-image (BSD 3-Clause)：https://scikit-image.org/ – （可选）用于增益图下采样。
- Python标准库：os、locale、numpy、torch、PIL、colorsys、re、glob、tempfile、subprocess
