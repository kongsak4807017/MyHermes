# Venue Checklists for Academic Figures

Standardized requirements for ML/AI conference and journal figures.

## NeurIPS

### Format
- Resolution: 300 DPI minimum
- Format: PDF (vector preferred) or PNG
- Font: Sans-serif (Helvetica, Arial, or equivalent)
- Font size: ≥ 8pt for all text

### Style
- Flat colors, no gradients
- No 3D effects or shadows
- Clean, minimal design
- Consistent line weights

### Content
- All axes labeled with units
- Legend if multiple series
- Error bars where applicable
- Colorblind-safe palette

## ICML

### Format
- Same as NeurIPS
- Slightly more color flexibility allowed

### Style
- Emphasize mathematical clarity
- Use notation consistent with paper
- Clear distinction between methods

### Content
- Statistical significance markers
- Confidence intervals where appropriate

## ACL

### Format
- Resolution: 300 DPI minimum
- Format: PDF or PNG

### Style
- Focus on sequential/linguistic structure
- Tree or chain layouts for NLP
- Token-level annotations where relevant

### Content
- Clear input/output examples
- Attention heatmaps with proper scaling

## IEEE

### Format
- Grayscale-safe by default
- Higher contrast requirements
- Figure captions in IEEE format

### Style
- Conservative, formal
- Assume monochrome printing
- Pattern fills for differentiation

### Content
- Figure number and caption below
- Source citations for data
- Error bars mandatory

## arXiv

### Format
- PDF (vector) strongly preferred
- Embedded fonts

### Style
- Flexible, but professional
- Consider both color and grayscale viewers

### Content
- Self-contained legends
- Clear axis labels

## Color Palettes

### NeurIPS/ICML Recommended
| Purpose | Hex | RGB |
|---------|-----|-----|
| Primary | #1f4e79 | (31, 78, 121) |
| Secondary | #2e8b8b | (46, 139, 139) |
| Accent | #ff6b35 | (255, 107, 53) |
| Success | #28a745 | (40, 167, 69) |
| Warning | #ffc107 | (255, 193, 7) |
| Background | #fafafa | (250, 250, 250) |
| Text | #333333 | (51, 51, 51) |
| Grid | #e0e0e0 | (224, 224, 224) |

### Grayscale-safe (IEEE)
| Purpose | Hex | Pattern |
|---------|-----|---------|
| Primary | #000000 | Solid |
| Secondary | #666666 | Dashed |
| Tertiary | #999999 | Dotted |
| Background | #ffffff | None |
| Text | #000000 | Solid |

## Common Pitfalls
1. Using color as the ONLY encoding (always add pattern/label backup)
2. Fonts too small for print (≥ 8pt rule)
3. Missing axis labels or units
4. Inconsistent notation between figure and text
5. Overcrowded diagrams (≤ 9 main elements recommended)
