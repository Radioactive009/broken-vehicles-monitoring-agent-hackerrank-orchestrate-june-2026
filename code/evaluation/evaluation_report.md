# Complete Evaluation Report

## Summary Metrics
| Metric | Accuracy (%) | Matches | Total |
| :--- | :--- | :--- | :--- |
| Claim status | 25.0% | 5 | 20 |
| Issue type | 15.0% | 3 | 20 |
| Object part | 5.0% | 1 | 20 |
| Severity | 15.0% | 3 | 20 |
| Evidence standard met | 85.0% | 17 | 20 |
| Valid image | 95.0% | 19 | 20 |

## Case by Case Prediction Details

### Row 1 (User: user_001, Object: CAR)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed rear_bumper is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `rear_bumper` | Predicted: `unknown`
- **Issue Match:** Expected: `dent` | Predicted: `unknown`

### Row 2 (User: user_002, Object: CAR)
- **Claim Status:** Expected: `not_enough_information` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed front_bumper is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `False` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `front_bumper` | Predicted: `unknown`
- **Issue Match:** Expected: `broken_part` | Predicted: `unknown`

### Row 3 (User: user_004, Object: CAR)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed windshield is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `windshield` | Predicted: `unknown`
- **Issue Match:** Expected: `crack` | Predicted: `unknown`

### Row 4 (User: user_007, Object: CAR)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed side_mirror is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `side_mirror` | Predicted: `unknown`
- **Issue Match:** Expected: `broken_part` | Predicted: `unknown`

### Row 5 (User: user_005, Object: CAR)
- **Claim Status:** Expected: `contradicted` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed rear_bumper is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `rear_bumper` | Predicted: `unknown`
- **Issue Match:** Expected: `scratch` | Predicted: `unknown`

### Row 6 (User: user_006, Object: CAR)
- **Claim Status:** Expected: `not_enough_information` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed headlight is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `False` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `headlight` | Predicted: `unknown`
- **Issue Match:** Expected: `unknown` | Predicted: `unknown`

### Row 7 (User: user_003, Object: CAR)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed door is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `door` | Predicted: `unknown`
- **Issue Match:** Expected: `dent` | Predicted: `unknown`

### Row 8 (User: user_008, Object: CAR)
- **Claim Status:** Expected: `contradicted` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed hood is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `False` | Predicted: `False`
- **Part Match:** Expected: `front_bumper` | Predicted: `unknown`
- **Issue Match:** Expected: `broken_part` | Predicted: `unknown`

### Row 9 (User: user_009, Object: LAPTOP)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed screen is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `screen` | Predicted: `unknown`
- **Issue Match:** Expected: `crack` | Predicted: `unknown`

### Row 10 (User: user_010, Object: LAPTOP)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed hinge is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `hinge` | Predicted: `unknown`
- **Issue Match:** Expected: `broken_part` | Predicted: `unknown`

### Row 11 (User: user_011, Object: LAPTOP)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed keyboard is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `keyboard` | Predicted: `unknown`
- **Issue Match:** Expected: `stain` | Predicted: `unknown`

### Row 12 (User: user_012, Object: LAPTOP)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed corner is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `corner` | Predicted: `unknown`
- **Issue Match:** Expected: `dent` | Predicted: `unknown`

### Row 13 (User: user_018, Object: LAPTOP)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed screen is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `screen` | Predicted: `unknown`
- **Issue Match:** Expected: `crack` | Predicted: `unknown`

### Row 14 (User: user_020, Object: LAPTOP)
- **Claim Status:** Expected: `contradicted` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed trackpad is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `trackpad` | Predicted: `unknown`
- **Issue Match:** Expected: `none` | Predicted: `unknown`

### Row 15 (User: user_015, Object: PACKAGE)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed package_corner is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `package_corner` | Predicted: `unknown`
- **Issue Match:** Expected: `crushed_packaging` | Predicted: `unknown`

### Row 16 (User: user_030, Object: PACKAGE)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed seal is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `seal` | Predicted: `unknown`
- **Issue Match:** Expected: `torn_packaging` | Predicted: `unknown`

### Row 17 (User: user_031, Object: PACKAGE)
- **Claim Status:** Expected: `supported` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed package_corner is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `package_side` | Predicted: `unknown`
- **Issue Match:** Expected: `water_damage` | Predicted: `unknown`

### Row 18 (User: user_032, Object: PACKAGE)
- **Claim Status:** Expected: `not_enough_information` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed contents is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `False` | Predicted: `True`
- **Image Usability:** Expected: `False` | Predicted: `True`
- **Part Match:** Expected: `contents` | Predicted: `unknown`
- **Issue Match:** Expected: `unknown` | Predicted: `unknown`

### Row 19 (User: user_033, Object: PACKAGE)
- **Claim Status:** Expected: `contradicted` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed box is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `unknown` | Predicted: `unknown`
- **Issue Match:** Expected: `unknown` | Predicted: `unknown`

### Row 20 (User: user_034, Object: PACKAGE)
- **Claim Status:** Expected: `contradicted` | Predicted: `contradicted`
- **Justification:** *"Claim contradicts image evidence. The claimed seal is visible but appears to have no damage."*
- **Evidence sufficiency:** Expected: `True` | Predicted: `True`
- **Image Usability:** Expected: `True` | Predicted: `True`
- **Part Match:** Expected: `seal` | Predicted: `unknown`
- **Issue Match:** Expected: `none` | Predicted: `unknown`

