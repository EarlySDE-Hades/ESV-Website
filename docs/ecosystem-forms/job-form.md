# Form: Job application

Read [README.md](README.md) first: it has the shared rules and the acceptance checklist.

**Build this only once Earlyseed Ventures has sent the list of open roles.** The careers page has none today, so nothing links here yet.

## Purpose

Someone on the website wants to apply for an open role on the careers page. One form serves every role. It is an application, and offers nobody a job.

The form must not mention pay, and must not ask for current or past salary.

## Form settings

| Setting | Value |
|---|---|
| Public link | `/apply/careers` |
| `form_title` (internal) | ESV Job Intake |
| `form_display_name` (public) | Job Application |
| `form_description` (public) | Tell us about yourself and the role you are applying for. |
| Pipeline | New: "Hiring" |

Proposed stages, first stage in bold: **New application** → Shortlisted → First interview → Second interview → Offer → Joined → Not now.

## Questions

"Next" is the following row unless a branch is given.

| # | Key | Question | Type | Options | Next |
|---|---|---|---|---|---|
| 1 | `role` | Which role are you applying for? | `mcq` | The open roles, worded as on the careers page | |
| 2 | `full_name` | What is your full name? | `short_text`, contact `name` | | |
| 3 | `email` | What is your email address? | `short_text`, contact `email` | | |
| 4 | `phone` | What is your phone number, with country code? | `short_text`, contact `phone` | | |
| 5 | `city` | Which city and country do you live in? | `short_text` | | |
| 6 | `current` | What do you do now? Tell us your role and organisation. | `short_text` | | |
| 7 | `experience` | How many years of relevant experience do you have? | `mcq` | Less than 1; 1 to 3; 3 to 5; 5 to 10; Over 10 | |
| 8 | `why` | Why this role, and why Earlyseed Ventures? | `long_text` | | |
| 9 | `work` | Tell us about a piece of work you are proud of, and your part in it. | `long_text` | | |
| 10 | `cv_link` | Share a link to your CV (for example Google Drive). Please make sure anyone with the link can open it. | `short_text` | | |
| 11 | `linkedin` | What is your LinkedIn profile? Type "None" if you don't have one. | `short_text` | | |
| 12 | `portfolio` | Do you have a portfolio or other work to show? Share a link, or type "None". | `short_text` | | |
| 13 | `mumbai` | Could you work from our Mumbai office? | `mcq` | Yes; Yes, if I can relocate; No; Some days | |
| 14 | `start` | When could you start? | `short_text` | | |
| 15 | `heard_from` | How did you hear about us? | `mcq` | LinkedIn; A referral; An event; Press or an article; Web search; Other | A referral → 16. All others → 17 |
| 16 | `referrer` | Who referred you? | `short_text` | | |
| 17 | `consent` | I agree to Earlyseed Ventures storing these details and contacting me about this role, as described in the privacy policy. | `mcq` | I agree | End |

**Roles (1).** When a role opens or closes, its option changes here and in the website's `tools/careers/openings.json`. Keep the wording identical. If no role is open, unpublish the form.

**If the app has a file upload type,** stop and ask before using it for 10: a link keeps CVs out of the app.

## Success screen

> **Thank you.**
> We have your application. Someone from our team will get in touch if there is a good fit.
>
> Earlyseed Ventures, info@earlyseedventures.com

Do not promise a response time.

## Branch walkthroughs to test

| Path | Answers | Screens seen |
|---|---|---|
| Shortest | 15 "LinkedIn" | 1–15, 17, End |
| Longest | 15 "A referral" | 1–17, End |
