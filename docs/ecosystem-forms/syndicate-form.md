# Form: Syndicate application

Read [README.md](README.md) first: it has the shared rules and the acceptance checklist.

## Purpose

Someone on the website wants to invest through the Earlyseed Ventures syndicate. The form gives the team enough to have a useful first conversation: who they are, how they invest and what they want to see. It is an expression of interest. It does not admit anyone to the syndicate and commits nobody to invest.

Context from the website: the minimum syndicate ticket is ₹5 Lakh, investors come in together on the same terms, and they decide deal by deal.

## Form settings

| Setting | Value |
|---|---|
| Public link | `/apply/syndicate` |
| `form_title` (internal) | ESV Syndicate Intake |
| `form_display_name` (public) | Syndicate Application |
| `form_description` (public) | Tell us a little about yourself and how you like to invest. Your answers go to the Earlyseed Ventures team, and submitting this form does not commit you to anything. |
| Pipeline | New: "Syndicate investors" |

Proposed stages, first stage in bold: **New application** → Contacted → Deep dive call → Onboarding and KYC → Active member → Not now. Use an existing investor pipeline instead if the app has one.

## Questions

"Next" is the following row unless a branch is given.

| # | Key | Question | Type | Options | Next |
|---|---|---|---|---|---|
| 1 | `full_name` | What is your full name? | `short_text`, contact `name` | | |
| 2 | `email` | What is your email address? | `short_text`, contact `email` | | |
| 3 | `phone` | What is your phone number, with country code? | `short_text`, contact `phone` | | |
| 4 | `location` | Which city and country do you live in? | `short_text` | | |
| 5 | `linkedin` | What is your LinkedIn profile? Type "None" if you don't have one. | `short_text` | | |
| 6 | `occupation` | What do you do? Tell us your role and organisation. | `short_text` | | |
| 7 | `investor_type` | How would you invest? | `mcq` | Individual, resident in India; Individual, NRI or OCI; Individual, foreign national; HUF; Company or LLP; Family office; Trust; Not sure yet | Company or LLP, Family office, Trust → 8. All others → 9 |
| 8 | `entity_name` | What is the name of the entity? | `short_text` | | |
| 9 | `invested_before` | Have you invested in start-ups before? | `mcq` | Yes; No, this would be my first | Yes → 10. No → 11 |
| 10 | `past_investments` | Roughly how many, and in which companies or sectors? Share only what you are comfortable with. | `long_text` | | |
| 11 | `ticket_size` | How much would you be comfortable investing in one start-up? | `mcq` | ₹5 Lakh to ₹10 Lakh; ₹10 Lakh to ₹25 Lakh; ₹25 Lakh to ₹50 Lakh; ₹50 Lakh to ₹1 Crore; Above ₹1 Crore; Not decided yet | |
| 12 | `deals_per_year` | How many start-ups would you like to invest in over the next 12 months? | `mcq` | 1; 2 to 3; 4 to 6; More than 6; Not decided yet | |
| 13 | `sector_first` | Which sector interests you most? | `mcq` | Open to any sector, then the list below | |
| 14 | `sector_second` | Is there a second sector that interests you? | `mcq` | No second sector, then the list below | |
| 15 | `stage` | Which stage would you prefer to invest at? | `mcq` | Idea or prototype; Early revenue; Growth; Pre-IPO; Open to any stage | |
| 16 | `goals` | What would you like from the syndicate, beyond access to deals? | `mcq` | Learning how to evaluate start-ups; Meeting other investors; Working with founders; Deal access only; All of these | |
| 17 | `heard_from` | How did you hear about us? | `mcq` | A referral; LinkedIn; An event; BNI; Press or an article; Web search; Other | A referral → 18. All others → 19 |
| 18 | `referrer` | Who referred you? | `short_text` | | |
| 19 | `notes` | Is there anything else we should know? Type "No" if not. | `long_text` | | |
| 20 | `risk_ack` | Investing in early-stage companies is high risk. You may lose all the money you invest, and shares in private companies can be hard to sell. Do you understand this? | `mcq` | Yes, I understand; I have questions first | |
| 21 | `consent` | I agree to Earlyseed Ventures storing these details and contacting me about its syndicate, as described in the privacy policy. | `mcq` | I agree | End |

**Sector list for 13 and 14.** Same labels and order as the founder form, so the two can be matched:
AgriTech; AI/ML; AR/VR; B2B; Beauty; BioTech; ClimateTech; Consumer; Cybersecurity; D2C; DeepTech; Defence; Drones; E-commerce; EdTech; Energy; EV & Mobility; Fashion; FinTech; FoodTech; Gaming; Hardware; HealthTech; HRTech; Infrastructure; IoT; LegalTech; Logistics; Manufacturing; Marketplace; Media; Real Estate; Retail; Robotics; SaaS; SpaceTech; Sports; Travel; Web3; Other

**If the app has a pick-several type:** merge 13 and 14 into one question, "Which sectors interest you?", with "Open to any sector" first. Make 15 and 16 pick-several too, and drop "All of these" from 16.

**"I have questions first" (20)** does not block submission. Flag it on the record so the team answers before anything else.

## Success screen

> **Thank you.**
> We have your details. Someone from our team will get in touch to learn how you like to invest.
>
> Earlyseed Ventures, info@earlyseedventures.com

Do not promise a response time, and do not mention deals.

## Branch walkthroughs to test

| Path | Answers | Screens seen |
|---|---|---|
| Shortest | 7 "Individual, resident in India", 9 "No", 17 "LinkedIn" | 1–7, 9, 11–17, 19–21, End |
| Longest | 7 "Family office", 9 "Yes", 17 "A referral" | 1–21, End |
| Questions first | As shortest, 20 "I have questions first" | Same as shortest, and the record is flagged |
