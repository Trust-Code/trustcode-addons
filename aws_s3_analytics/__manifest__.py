{  # pylint: disable=C8101,C8103,C7902
    "name": "AWS S3 analytics",
    "description": """Análise dos buckets de backup.""",
    "author": "Trustcode",
    "category": "Productivity",
    "version": "14.0.0.2",
    "contributors": [""],
    "depends": ['mail'],
    "data": [
        "views/buckets.xml",
        "views/res_company.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "data/decimal_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto-install": False,
}
