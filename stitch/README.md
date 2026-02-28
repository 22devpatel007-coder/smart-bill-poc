# Stitch Design System

This folder contains the UI layout designs for the Smart POS application, intended to be generated using [Stitch](https://stitch.withgoogle.com).

## Folder Structure
- **`design_system/`**: Global styles (Typography, Colors, Component Samples).
- **`screens/`**: Complete 1280x800px UI screen mockups.
- **`components/`**: Reusable micro-layouts (e.g. `stat_card.png`, `search_bar.png`).
- **`reference_photos/`**: Inspirational real-world images to guide the AI design generation.

## How to Generate Screen Designs
1. Go to Google Images and search for the reference query (e.g., `"simple pos software login screen"`).
2. Download a high-quality, professional enterprise software screenshot (avoid mobile UI or heavily stylized gradients).
3. Save it inside the `reference_photos/` folder.
4. Open [stitch.withgoogle.com](https://stitch.withgoogle.com).
5. Drag the reference photo into Stitch.
6. Copy the specific screen prompt from your design guide and paste it into Stitch. Append the instruction: *"Use this image as a layout reference but apply the Smart POS color scheme and Indian data"*.
7. Generate and export the result as a PNG.
8. Save the PNG to the `stitch/screens/` folder.

## The Global Design Prompt
To maintain consistency across all screens, always prepend this base prompt to your Stitch sessions:
> Design for a Windows desktop POS app at 1280x800px used by Indian shop cashiers. Font: Inter (or Segoe UI). Colors: Navy #1E3A5F (sidebar/header), Blue #2563EB (actions), Amber #F59E0B (primary CTA like Print Bill), Green #10B981 (success), Red #EF4444 (error). Background: #F8FAFC. Cards: white, 8px radius, 1px #E2E8F0 border. Inputs: 40px height, 6px radius. NO gradients. NO illustrations. Simple and functional. Sidebar: 220px wide, #1E3A5F background, white text. Topbar: 56px, #1E3A5F. Style: clean enterprise software — like Tally or Zoho Books but simpler.
