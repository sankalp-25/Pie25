import pandas as pd

# Company data
company_data = pd.DataFrame({
    "company_name": [
        "20 Microns Limited", "21st Century Management Services Limited", 
        "360 ONE WAM LIMITED", "3i Infotech Limited", "3M India Limited", 
        "3P Land Holdings Limited", "3rd Rock Multimedia Limited", 
        "5Paisa Capital Limited", "63 moons technologies limited"
    ],
    "short_company_name": [
        "20MICRONS", "21STCENMGM", "360ONE", "3IINFOLTD", "3MINDIA", 
        "3PLAND", "3RDROCK", "5PAISA", "63MOONS"
    ]
})

# Save DataFrame to CSV
company_data.to_csv("company_data.csv", index=False)
print("Company data saved to company_data.csv")
