# Form: Strategic Growth Partner (SGP) application

Read [README.md](README.md) first: it has the shared rules and the acceptance checklist.

## Purpose

Someone on the website wants to become a Strategic Growth Partner. SGPs are industry leaders who mentor founders, open doors and build alongside Earlyseed Ventures. The form tells the team what the person would bring and where, before a conversation with the co-founders. It is an expression of interest and appoints nobody.

Commercial terms are agreed one to one. The form must not mention fees, revenue share, equity or territory rights.

## Form settings

| Setting | Value |
|---|---|
| Public link | `/apply/partner` |
| `form_title` (internal) | ESV Growth Partner Intake |
| `form_display_name` (public) | Strategic Growth Partner Application |
| `form_description` (public) | Tell us about your background, your network and how you would like to work with founders. Your answers go to the Earlyseed Ventures team. |
| Pipeline | New: "Growth partners" |

Proposed stages, first stage in bold: **New application** → Contacted → Meeting with co-founders → Terms → Orientation → Active partner → Not now.

## Questions

"Next" is the following row unless a branch is given.

| # | Key | Question | Type | Options | Next |
|---|---|---|---|---|---|
| 1 | `full_name` | What is your full name? | `short_text`, contact `name` | | |
| 2 | `email` | What is your email address? | `short_text`, contact `email` | | |
| 3 | `phone` | What is your phone number, with country code? | `short_text`, contact `phone` | | |
| 4 | `location` | Which city and country do you live in? | `short_text` | | |
| 5 | `linkedin` | What is your LinkedIn profile? Type "None" if you don't have one. | `short_text` | | |
| 6 | `role_org` | What is your current role and organisation? | `short_text` | | |
| 7 | `experience_years` | How many years of professional experience do you have? | `mcq` | Under 10; 10 to 20; 20 to 30; Over 30 | |
| 8 | `field` | Which field best describes your work? | `mcq` | Business coaching or advisory; Finance, banking or lending; Law or intellectual property; Marketing or sales; Technology; Manufacturing or industry; Healthcare; Education or campus; Real estate or infrastructure; Government or public sector; Other | |
| 9 | `background` | Tell us about your background, in a few sentences. | `long_text` | | |
| 10 | `contribution` | How would you most like to help? | `mcq` | Mentoring founders; Opening doors to customers and industry; Introducing investors; Finding promising start-ups; Supporting campus programmes; A mix of these | |
| 11 | `region` | Which region do you know best? | `mcq` | Mumbai; Rest of West India; North India; South India; East or North-East India; Central India; UAE; Elsewhere outside India | Elsewhere outside India → 12. All others → 13 |
| 12 | `region_other` | Which country or region? | `short_text` | | |
| 13 | `network` | Describe your network: the industries, business groups or communities you are active in. Please don't name private individuals. | `long_text` | | |
| 14 | `startup_experience` | Have you mentored, advised or invested in start-ups before? | `mcq` | Yes; No | Yes → 15. No → 16 |
| 15 | `startup_details` | Tell us briefly about that work. | `long_text` | | |
| 16 | `other_roles` | Do you hold a role with another fund, angel network, accelerator or start-up platform? | `mcq` | Yes; No | Yes → 17. No → 18 |
| 17 | `other_roles_details` | Which one, and what is your role? | `long_text` | | |
| 18 | `time` | How much time could you give in a typical month? | `mcq` | A few hours; 1 to 2 days; 3 to 5 days; More than 5 days; Not sure yet | |
| 19 | `why` | Why would you like to be a Strategic Growth Partner? | `long_text` | | |
| 20 | `syndicate_interest` | Would you also like to hear about investing through our syndicate? | `mcq` | Yes; Maybe later; No | |
| 21 | `heard_from` | How did you hear about us? | `mcq` | A current growth partner; Another referral; LinkedIn; An event; BNI; Press or an article; Web search; Other | A current growth partner, Another referral → 22. All others → 23 |
| 22 | `referrer` | Who referred you? | `short_text` | | |
| 23 | `consent` | I agree to Earlyseed Ventures storing these details and contacting me about becoming a partner, as described in the privacy policy. | `mcq` | I agree | End |

**If the app has a pick-several type:** use it for 10 and 11, and drop "A mix of these" from 10.

**Syndicate interest (20).** "Yes" should tag the contact "Syndicate interest". It must not create a syndicate application or count as consent to syndicate emails: the team follows up in person.

**Other roles (16, 17)** help the team spot conflicts of interest. They never reject an application automatically.

## Success screen

> **Thank you.**
> We have your details. Someone from our team will get in touch to arrange a conversation.
>
> Earlyseed Ventures, info@earlyseedventures.com

Do not promise a response time.

## Branch walkthroughs to test

| Path | Answers | Screens seen |
|---|---|---|
| Shortest | 11 "Mumbai", 14 "No", 16 "No", 21 "LinkedIn" | 1–11, 13, 14, 16, 18–21, 23, End |
| Longest | 11 "Elsewhere outside India", 14 "Yes", 16 "Yes", 21 "A current growth partner" | 1–23, End |
| Syndicate interest | As shortest, 20 "Yes" | Same as shortest, and the contact is tagged |
