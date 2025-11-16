“Opora” (Опора) — A Web App for Access to Benefits and Discounts for Vulnerable Groups
Build a responsive web application (installable as a PWA) aimed at vulnerable populations—seniors, people with disabilities, large families, low‑income households, etc.—that provides personalized access to:
Government benefits (social payments, medicines, transport, utilities, education, etc.)
Commercial offers from private companies (discounts at pharmacies, grocery stores, household services, etc.)

The app must be simple, accessible, secure, and work on low‑end devices (including older smartphones).

Core Requirements
1) Registration and Personalization
Registration options:

Email + SMS/e-signature, or
Via the **Gosuslugi account (OAuth — a mock implementation is acceptable)

During registration, the user specifies:

Beneficiary category (choose: pensioner, disability group 1/2/3, parent of many children, veteran, low‑income, etc.)
Region of residence (required for regional benefits)
*SNILS number (optional but recommended)

Ability to verify beneficiary status:

Automatic verification via API (mock or integration with a test service is a plus)

Data must be stored and transmitted with privacy safeguards (HTTPS, *SNILS masking, consent for personal data processing).

2) Personal Dashboard
Display:

Active benefits (labelled as federal / regional / municipal)
Recommended partner promotions and discounts
Validity periods (highlight those expiring soon)

Capabilities:

Hide/mark non‑relevant benefits
Add interest categories (e.g., “medicine benefits”)
Export the benefits list to PDF / print format (for visiting service centers)


3) Search and Filtering

Smart keyword search (“medicines”, “transport”, “compensation”)

Filters:

By type: government / commercial
By beneficiary category
By region
By status: active / expiring soon / requires verification

Sorting:

By relevance, date, popularity


4) Benefits and Deals Database
You need to make a data parser from next urls (we will also add some features to auto-parse the actual data from the resources):
https://sfr.gov.ru/grazhdanam/pensionres/
https://sfr.gov.ru/grazhdanam/semyam_s_detmi/
https://sfr.gov.ru/grazhdanam/invalidam/
https://sfr.gov.ru/grazhdanam/Informaciya_dlya_uchastnikov_SVO_i_ih_semei/
https://sfr.gov.ru/grazhdanam/victims_of_industrial_accidents/
https://sfr.gov.ru/grazhdanam/newregion/
https://sfr.gov.ru/grazhdanam/pensionres/pens_sssr/
https://sfr.gov.ru/grazhdanam/pensionres/pens_zagran/
https://sfr.gov.ru/grazhdanam/workers/
https://sfr.gov.ru/grazhdanam/eln/
https://sfr.gov.ru/grazhdanam/social_support/
https://sfr.gov.ru/grazhdanam/cosp/


Internal database (mock data in JSON/CSV is acceptable, but must be structured and realistic)
At least 15 benefits (federal + regional, e.g., for Yakutsk)
At least 10 commercial partner offers (pharmacies, stores, utilities services)

In our project, for the MVP there is a Sqlite DB, but in future it can be easily increased by PostGRES or Supabase. 

Required fields for each record:
{
  "id": "pens-transport-2025",
  "title": "Free Public Transport",
  "type": "federal",
  "target_groups": ["pensioner", "disabled"],
  "region": ["all", "77", "54"],
  "valid_from": "2025-01-01",
  "valid_to": "2025-12-31",
  "requirements": "Beneficiary ID required",
  "how_to_get": "Apply at a service center with passport and beneficiary ID",
  "source_url": "https://mintrud.gov.ru/...",
  "partner": null
}

Technology Stack
Fast loading (optimized for 3G/low‑end devices)
Responsiveness and accessibility (WCAG — at least basics: contrast, large font, keyboard navigation). 
For example you can check settings_example.PNG:
- font-size: Normal, Enlarged, Huge
- font-family: Sans-serif, Serif
- Letter spacing: Normal, Enlarged, Huge
- Color mode: Monochrome, Monochromatic Inversion, Blue Background
- Switch images: On, Off
- Speech assistant: Play, Stop, Repeat
Reset settings to default button
Select a piece of text and press Ctrl+ENTER for voice.

Frontend: Nuxt
Backend: Python (Django)
Database: SQLite (aiosqlite) 
Hosting: local for testing and VPS for deploy

*Individual insurance account number (SNILS) is a number issued and used by the Pension Fund of the Russian Federation to residents of Russia for the purpose of tracking their social security accounts.
**The Federal State Information System "Unified Portal of State and Municipal Services (Functions)" (Russian: Федеральная государственная информационная система «Единый портал государственных и муниципальных услуг (функций)»), commonly referred to as Gosuslugi (Russian: Госуслуги), is a digital platform operated by the Russian government.
