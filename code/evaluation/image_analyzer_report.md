# Production Image Analyzer Evaluation Report

## Normalization Mappings
The `ImageAnalyzer` normalizes raw VLM responses using python-based substring dictionaries:

### Objects
- `cardboard box`, `shipping box`, `box`, `carton`, `parcel` -> `package`
- `automobile`, `vehicle`, `sedan`, `suv`, `truck` -> `car`
- `notebook`, `macbook`, `pc`, `computer` -> `laptop`

### Issues
- `collision`, `impact damage`, `bumper dent`, `dented` -> `dent`
- `scrape`, `scuff`, `abrasion` -> `scratch`
- `fracture`, `split` -> `crack`
- `shattered glass`, `broken screen`, `shattered screen` -> `glass_shatter`
- `physical damage`, `crushed`, `crushed corner`, `smashed` -> `crushed_packaging`
- `torn`, `ripped`, `torn box` -> `torn_packaging`
- `leak`, `spill` -> `water_damage`

### Parts
- `trunk bumper`, `back bumper`, `rear bumper and trunk` -> `rear_bumper`
- `front fascia`, `front bumper area` -> `front_bumper`
- `display`, `panel`, `lcd` -> `screen`
- `key`, `keys` -> `keyboard`
- `track pad`, `mousepad` -> `trackpad`
- `corner of box`, `box corner` -> `package_corner`
- `side of box`, `box side` -> `package_side`

## Prompts & Schema
The analyzer uses a strict prompt structure requesting a structured JSON payload with fields:
- `detected_object`
- `visible_issue_type`
- `visible_object_part`
- `damage_visible`
- `severity`
- `image_quality`
- `risk_flags`
- `supporting_image_ids`

## Example Outputs & Comparisons

### Case 0 (CAR)
- **Image Paths:** `images/sample/case_001/img_1.jpg`
- **Expected Ground Truth:**
  - Issue Type: `dent`
  - Object Part: `rear_bumper`
  - Expected Risk Flags: `none`
- **Image Analyzer Output:**
```json
{
  "detected_object": "car",
  "visible_issue_type": "unknown",
  "visible_object_part": "rear_bumper",
  "damage_visible": false,
  "severity": "high",
  "image_quality": "clear",
  "risk_flags": [
    "damage_not_visible"
  ],
  "supporting_image_ids": [
    "img_1"
  ]
}
```

### Case 1 (CAR)
- **Image Paths:** `images/sample/case_002/img_1.jpg;images/sample/case_002/img_2.jpg`
- **Expected Ground Truth:**
  - Issue Type: `broken_part`
  - Object Part: `front_bumper`
  - Expected Risk Flags: `wrong_object;claim_mismatch;manual_review_required`
- **Image Analyzer Output:**
```json
{
  "detected_object": "car",
  "visible_issue_type": "broken_part",
  "visible_object_part": "front_bumper",
  "damage_visible": true,
  "severity": "medium",
  "image_quality": "cropped",
  "risk_flags": [
    "cropped_or_obstructed"
  ],
  "supporting_image_ids": [
    "img_1"
  ]
}
```

### Case 8 (LAPTOP)
- **Image Paths:** `images/sample/case_009/img_1.jpg`
- **Expected Ground Truth:**
  - Issue Type: `crack`
  - Object Part: `screen`
  - Expected Risk Flags: `none`
- **Image Analyzer Output:**
```json
{
  "detected_object": "laptop",
  "visible_issue_type": "glass_shatter",
  "visible_object_part": "screen",
  "damage_visible": true,
  "severity": "high",
  "image_quality": "clear",
  "risk_flags": [],
  "supporting_image_ids": [
    "img_1"
  ]
}
```

### Case 9 (LAPTOP)
- **Image Paths:** `images/sample/case_010/img_1.jpg;images/sample/case_010/img_2.jpg`
- **Expected Ground Truth:**
  - Issue Type: `broken_part`
  - Object Part: `hinge`
  - Expected Risk Flags: `none`
- **Image Analyzer Output:**
```json
{
  "detected_object": "laptop",
  "visible_issue_type": "broken_part",
  "visible_object_part": "screen",
  "damage_visible": true,
  "severity": "high",
  "image_quality": "cropped",
  "risk_flags": [
    "cropped_or_obstructed",
    "low_light_or_glare"
  ],
  "supporting_image_ids": [
    "img_1"
  ]
}
```

### Case 14 (PACKAGE)
- **Image Paths:** `images/sample/case_015/img_1.jpg`
- **Expected Ground Truth:**
  - Issue Type: `crushed_packaging`
  - Object Part: `package_corner`
  - Expected Risk Flags: `none`
- **Image Analyzer Output:**
```json
{
  "detected_object": "package",
  "visible_issue_type": "crushed_packaging",
  "visible_object_part": "package_corner",
  "damage_visible": true,
  "severity": "medium",
  "image_quality": "cropped",
  "risk_flags": [
    "cropped_or_obstructed"
  ],
  "supporting_image_ids": [
    "img_1"
  ]
}
```

## Failure Cases and Mitigations
- **VLM Ambiguities:** When a VLM identifies a general issue (e.g. 'physical damage'), we resolve it to specific taxonomy classes (e.g. 'crushed_packaging') based on the context of the claim object (Cars vs. Laptops vs. Packages).
- **Implicit Verification:** If the VLM fails to flag mismatches or no damage, our post-processing logic validates object/part agreement programmatically and injects appropriate risk flags (`wrong_object`, `wrong_object_part`, `damage_not_visible`).
