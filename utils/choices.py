APPT_HOLIDAYS = [
    ("NewYear", "New Year's Day"),
    ("Memorial", "Memorial Day"),
    ("Independence", "Independence Day"),
    ("Labor", "Labor Day"),
    ("Thanksgiving", "Thanksgiving Day"),
    ("Christmas", "Christmas Day"),
]

APPT_STATUS = [
    ("Open", "Open"),
    ("Reserved", "Reserved"),
    ("Confirmed", "Confirmed"),
    ("Completed", "Completed"),
    ("Canceled", "Canceled"),
    ("NoShow", "NoShow"),
]

ARTICLE_TYPE = [
    ("ABOUT", "ABOUT"),
    ("PHOTOS", "PHOTOS"),
    ("WORKHOUR", "WORKHOUR"),
    ("SERIVE", "SERVICE"),
    ("INSURANCE", "INSURANCE"),
    ("EQUIPMENT", "EQUIPMENT"),
    ("MARKETING", "MARKETING"),
    ("OTHERS", "OTHERS"),
]

APPT_RULES = [
    ("Weekday", "Weekday"),
    ("Holiday", "Holiday"),
    ("Dayhour", "Dayhour"),
]
APPT_DAYS = [
    ("0", "Sunday"),
    ("1", "Monday"),
    ("2", "Tuesday"),
    ("3", "Wednesday"),
    ("4", "Thursday"),
    ("5", "Friday"),
    ("6", "Saturday"),
]

APPT_HOURS = [
    (7, "07:00"),
    (8, "08:00"),
    (9, "09:00"),
    (10, "10:00"),
    (11, "11:00"),
    (12, "12:00"),
    (13, "13:00"),
    (14, "14:00"),
    (15, "15:00"),
    (16, "16:00"),
    (17, "17:00"),
    (18, "18:00"),
    (19, "19:00"),
    (20, "20:00"),
    (21, "21:00"),
]
APPT_TIME_UNITS = [
    (10, "10 minutes"),
    (15, "15 minutes"),
    (20, "20 minutes"),
    (30, "30 minutes"),
    (60, "60 minutes"),
]


STATE_CHOICES = (
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AS", "American Samoa"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District Of Columbia"),
    ("FM", "Federated States Of Micronesia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("GU", "Guam"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MH", "Marshall Islands"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("MP", "Northern Mariana Islands"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PW", "Palau"),
    ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VI", "Virgin Islands"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
)

GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Unknown", "Unknown"),
)
# GENDER_CHOICES = (("Male", "Male"), ("Female", "Female"), ("Unknown", "Unknown"))

USER_CATEGORY_CHOICES = (
    ("Doctor", "Doctor"),
    ("Imaging", "Imaging Provider"),
    ("Both", "Both"),
)

USER_EMPLOYEE_CHOICES = (
    ("Customer", "Customer"),
    ("Staff", "Staff"),
)

APP_CHOICES = (
    ("HPACS", "HPACS"),
    ("CBCT", "CBCT"),
    ("SAVVY", "SAVVY"),
    ("SHOP", "SHOP"),
)

FILETYPE_CHOICES = [
    ("Image", "Image"),
    ("Video", "Video"),
    ("Document", "Document"),
    ("Others", "Others"),
]
MODALITY_CHOICES = [
    ("IOCamera", "IO Camera"),
    ("IOXray", "IO Xray"),
    ("Pano", "Panoramic"),
    ("CBCT", "CBCT"),
    ("Ceph", "Cephalometric"),
    ("Camera", "Camera"),
    ("Others", "Others"),
]
TOOTH_CHOICES = [
    ("1", "01"),
    ("2", "02"),
    ("3", "03"),
    ("4", "04"),
    ("5", "05"),
    ("6", "06"),
    ("7", "07"),
    ("8", "08"),
    ("9", "09"),
    ("10", "10"),
    ("11", "11"),
    ("12", "12"),
    ("13", "13"),
    ("14", "14"),
    ("15", "15"),
    ("16", "16"),
    ("17", "17"),
    ("18", "18"),
    ("19", "19"),
    ("20", "20"),
    ("21", "21"),
    ("22", "22"),
    ("23", "23"),
    ("24", "24"),
    ("25", "25"),
    ("26", "26"),
    ("27", "27"),
    ("28", "28"),
    ("29", "29"),
    ("30", "30"),
    ("31", "31"),
    ("32", "32"),
    ("99", "Others"),
]
PANO_SECTION_CHOICES = [
    ("050", "2D Visualized Report"),
    ("100", "Panoramic View"),
    ("200", "Upper Left"),
    ("300", "Upper Center"),
    ("400", "Upper Right"),
    ("500", "Lower Right"),
    ("600", "Lower Center"),
    ("700", "Lower Left"),
    ("900", "Others"),
]
TOOTH_QUADRANT_CHOICES = [
    ("UR", "Upper Right"),
    ("UL", "Upper Left"),
    ("LR", "Lower Right"),
    ("LL", "Lower Left"),
    ("Others", "Others"),
]
TOOTH_SECTION_CHOICES = [
    ("Anterior", "Anterior"),
    ("Premolar", "Premolar"),
    ("Molar", "Molar"),
    ("Others", "Others"),
]
TOOTH_SURFACE_CHOICES = [
    ("B", "Buccal"),
    ("D", "Distal"),
    ("F", "Facial"),
    ("I", "Incisal"),
    ("L", "Lingual"),
    ("M", "Mesial"),
    ("O", "Occlusal"),
    ("P", "Palatal"),
    ("Others", "Others"),
]

STATUS_CHOICES = [
    ("Requested", "Requested"),
    ("Confirmed", "Confirmed"),
    ("Processing", "Processing"),
    ("Completed", "Completed"),
    ("Canceled", "Canceled"),
]

CATEGORY_CHOICES = [
    ("Implant", "Implant"),
    ("Extraction", "Extraction"),
    ("Trauma", "Trauma"),
    ("TMJ", "TMJ"),
    ("Surgery", "Oral Surgery"),
    ("Others", "Others"),
]
ROI_CHOICES = [
    ("Maxilla", "Maxilla"),
    ("Mandible", "Mandible"),
    ("Both", "Maxilla-Mandible"),
    ("Others", "Others"),
]

CASE_NAME_CHOICES = [
    ("CBCT", "CBCT"),
    ("Pano", "Pano"),
    ("Ceph", "Ceph"),
    ("Others", "Others"),
]

PAYMENT_METHOD_CHOICES = [
    ("Cash", "Cash"),
    ("CreditCard", "Credit Card"),
    ("Zelle", "Zelle"),
    ("Paypal", "Paypal"),
    ("Check", "Check"),
    ("BankTransfer", "Bank Transfer"),
    ("Others", "Others"),
]

HOLIDAY_CATEGORY = [
    ("N", "National"),
    ("C", "Company"),
    ("P", "Personal"),
]

TERM_CATEGORY = [
    ("D", "Daily"),
    ("W", "Weekly"),
    ("M", "Monthly"),
    ("Y", "Yearly"),
]

WORKHOURS = [
    (9, "9"),
    (10, "10"),
    (11, "11"),
    (12, "12PM"),
    (13, "1"),
    (14, "2"),
    (15, "3"),
    (16, "4"),
    (17, "5"),
    (99, "All Day"),
]

CONTRACT_STATUS = [
    ("A", "Active"),
    ("P", "PartTime"),
    ("I", "Inactive"),
    ("T", "Terminated"),
]

OPPORTUNITY_CATEGORY = [
    ("Sale", "Sale"),
    ("Support", "Support"),
    ("Issue", "Issue"),
]

OPPORTUNITY_STAGE = [
    ("Potential", "Potential"),
    ("Qualified", "Qualified"),
    ("Working", "Working"),
    ("Won", "Won"),
    ("Pending", "Pending"),
    ("Lost", "Lost"),
]

GENDER = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]

REFER_STATUS = [
    ("Draft", "Draft"),
    ("Requested", "검사요청"),
    ("Scheduled", "검사예약"),
    ("Cancelled", "검사취소"),
    ("Interpreted", "1차판독완료"),
    ("Cosigned", "2차판독완료"),
    ("Archived", "정산완료"),
]

TASK_STATUS = [
    ("Todo", "Todo"),
    ("Doing", "Doing"),
    ("Done", "Done"),
    ("Cancelled", "Cancelled"),
]
