# Form: Internship application

Read [README.md](README.md) first: it has the shared rules and the acceptance checklist.

## Purpose

Someone on the website wants to intern at Earlyseed Ventures. Applications are open all year, so this form has no closing date and stays published. It is an application, and offers nobody a place.

The form must not mention pay, stipend, duration or location of the internship: these are agreed with each intern.

## Form settings

| Setting | Value |
|---|---|
| Public link | `/apply/intern` |
| `form_title` (internal) | ESV Internship Intake |
| `form_display_name` (public) | Internship Application |
| `form_description` (public) | Tell us about yourself and the team you would like to join. Applications are open all year. |
| Pipeline | New: "Interns" |

Proposed stages, first stage in bold: **New application** → Shortlisted → Interview → Offer → Intern → Completed → Not now.

## Questions

"Next" is the following row unless a branch is given.

| # | Key | Question | Type | Options | Next |
|---|---|---|---|---|---|
| 1 | `full_name` | What is your full name? | `short_text`, contact `name` | | |
| 2 | `email` | What is your email address? | `short_text`, contact `email` | | |
| 3 | `phone` | What is your phone number, with country code? | `short_text`, contact `phone` | | |
| 4 | `age_18` | Are you 18 or older? | `mcq` | Yes; No | |
| 5 | `city` | Which city do you live in? | `short_text` | | |
| 6 | `status` | What are you doing at the moment? | `mcq` | Studying; Recently graduated; Working; Other | Studying, Recently graduated → 7. All others → 8 |
| 7 | `college` | Which college or university, which course, and which year? | `short_text` | | |
| 8 | `team` | Which team would you most like to join? | `mcq` | Investments; Investor relations; Design and communications; Bootcamps and events; Not sure yet | |
| 9 | `why` | Why would you like to intern with us? | `long_text` | | |
| 10 | `work` | Tell us about something you have made, studied or worked on that we should know about. | `long_text` | | |
| 11 | `cv_link` | Share a link to your CV (for example Google Drive). Please make sure anyone with the link can open it. | `short_text` | | |
| 12 | `linkedin` | What is your LinkedIn profile? Type "None" if you don't have one. | `short_text` | | |
| 13 | `portfolio` | Do you have a portfolio or other work to show? Share a link, or type "None". | `short_text` | | |
| 14 | `start` | When could you start? | `short_text` | | |
| 15 | `length` | How long could you intern for? | `mcq` | 1 month; 2 months; 3 months; 4 to 6 months; More than 6 months; Not sure yet | |
| 16 | `time` | How much time could you give? | `mcq` | Full-time; Part-time; Flexible | |
| 17 | `mumbai` | Could you work from our Mumbai office? | `mcq` | Yes; Yes, if I can relocate; No; Some days | |
| 18 | `heard_from` | How did you hear about us? | `mcq` | A bootcamp or my campus; LinkedIn; An event; A referral; Press or an article; Web search; Other | A referral → 19. All others → 20 |
| 19 | `referrer` | Who referred you? | `short_text` | | |
| 20 | `consent` | I agree to Earlyseed Ventures storing these details and contacting me about internships, as described in the privacy policy. | `mcq` | I agree | End |

**Team options (8)** match the four teams on the website. If they change on one side, change the other.

**If the app has a file upload type,** stop and ask before using it for 11: a link keeps CVs out of the app.

**"No" to 4** does not block submission. Flag it on the record, so the team asks for a parent's or guardian's consent before doing anything else.

## Success screen

> **Thank you.**
> We have your application. Someone from our team will get in touch if there is a good fit.
>
> Earlyseed Ventures, info@earlyseedventures.com

Do not promise a response time.

## Branch walkthroughs to test

| Path | Answers | Screens seen |
|---|---|---|
| Shortest | 6 "Working", 18 "LinkedIn" | 1–6, 8–18, 20, End |
| Longest | 6 "Studying", 18 "A referral" | 1–20, End |
| Under 18 | As shortest, 4 "No" | Same as shortest, and the record is flagged |
