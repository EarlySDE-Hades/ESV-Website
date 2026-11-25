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
| 4 | `age_18` | Are you 18 or older? | `mcq` | Yes; No | No → End (under 18). Yes → 5 |
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

**"No" to 4 (as built, replacing the first version of this spec)** ends the form. It shows a message asking a parent or guardian to email info@earlyseedventures.com, and stores nothing: no submission, no contact and no HR task. The privacy policy says our forms are for adults.

## HR task

**New. The form is already published: add this to it without changing its questions, link or pipeline.**

Every submission creates one task for HR, using the app's existing tasks. If the app has no task feature, or tasks can't be created from a form submission, stop and ask before building one.

| Field | Value |
|---|---|
| Title | Review internship application: {`full_name`} ({`team`}) |
| Assigned to | Dhwani Joshi (HR), by user account, not by name. Keep the assignee in one setting, so it can be changed without a code change. If there is no such account, or more than one, stop and ask. |
| Due | 2 weeks (14 calendar days) after the submission date, India time |
| Priority | Normal |
| Status | The app's "to do" status |
| Linked to | The submission and the contact, so HR can open both from the task |
| Description | The summary below |

Description, in this order, with the label before each answer:

- Team: `team`
- Status: `status`, and `college` if answered
- City: `city`. Mumbai office: `mumbai`
- Can start: `start`. For: `length`, `time`
- CV: `cv_link`. LinkedIn: `linkedin`. Portfolio: `portfolio`
- Heard from: `heard_from`, and `referrer` if answered

Show answers as plain text. Make a link clickable only if it starts with `http://` or `https://`, and never fetch or preview it: anyone can submit this form. Leave out the email, phone and long answers, which stay on the submission.

**Under 18 ("No" to 4).** Nothing is stored, so no task is created.

**Rules**
- One task per submission. A retry or double-click must not create a second one. If the same person applies again, that is a new submission and a new task.
- The submission is saved first. If creating the task fails, the applicant still sees the success screen, the failure is logged and the task is retried.
- The task is internal. The applicant never sees it, and it sends them nothing.
- Only people who can already see the submission can see the task.
- If the assignee's account is deactivated or missing, still create the task, unassigned, and flag it to an admin.
- Closing the task does not move the applicant through the pipeline, and moving the applicant does not close it.
- Use the app's usual notification for an assigned task. Don't add a new one.
- Submissions from before this change: don't create tasks. Tell us how many there are.

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
| Under 18 | 4 "No" | 1–4, End (under 18). Nothing is stored |

## HR task checks

- [ ] The shortest and longest walkthroughs above each create exactly one task, with every field as in the table.
- [ ] The under 18 walkthrough creates no submission, contact or task.
- [ ] A submission on 1 December is due on 15 December, including one made late at night India time.
- [ ] A double-click on submit creates one submission and one task.
- [ ] With task creation forced to fail, the submission is kept, the success screen shows, and the task appears after the retry.
- [ ] A CV answer of `javascript:alert(1)` or `<b>x</b>` appears as plain text.
- [ ] The task is assigned to Dhwani Joshi and appears in her task list.
- [ ] With no valid assignee, the task is still created, unassigned and flagged.
- [ ] HR can open the submission from the task. Someone without access to the submission can't see the task.
- [ ] The other forms create no HR tasks.
- [ ] Test submissions and tasks are removed afterwards.
