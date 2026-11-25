# Public forms for the ecosystem app

**For:** the coding agent working on `ecosystem.earlyseedventures.com`
**From:** the Earlyseed Ventures website (`www.earlyseedventures.com`)

The website has pages with application buttons. Each button needs a public form in the ecosystem app. The syndicate and SGP forms are built and published. The internship form is published too. **Still to do: the HR task on the internship form, and the job form.**

| Form | Website page | Public link the website expects | Spec | Status |
|---|---|---|---|---|
| Syndicate application | `/invest.html` | `https://ecosystem.earlyseedventures.com/apply/syndicate` | [syndicate-form.md](syndicate-form.md) | Published |
| Strategic Growth Partner (SGP) application | `/invest.html` | `https://ecosystem.earlyseedventures.com/apply/partner` | [partner-form.md](partner-form.md) | Published |
| Internship application | `/careers.html` | `https://ecosystem.earlyseedventures.com/apply/intern` | [internship-form.md](internship-form.md) | Published. **To add: HR task** |
| Job application | `/careers.html` | `https://ecosystem.earlyseedventures.com/apply/careers` | [job-form.md](job-form.md) | To build once there are open roles |

Read this file first. It holds everything the forms share.

## Scope

Build:

1. Each form marked "To build", and each "To add" item, using the form system that already serves the founder form at `/apply`.
2. One public link for each, at the paths above.
3. A pipeline for each, so submissions arrive somewhere the team can work them.

Do not change the founder form (`ESV Founder Intake`), the published forms, their links or their pipelines, except for a "To add" item in the table.

## What we know about the existing form system

This comes from reading the public founder form page on 25 November 2026. The app's own code was not available, so **check each point against the codebase, and follow the codebase where they differ.**

- `/apply` serves the founder form. `/apply/<slug>` is a public route: an unknown slug returns "Form not available". On that date, `/apply/intern` and `/apply/careers` both did.
- Other paths, such as `/invest` and `/partner`, redirect to `/login`. Keep the new forms under `/apply/`, so no sign-in is needed.
- A form has `form_id`, `form_title` (internal), `form_display_name` (public), `form_description`, `link_id`, `pipeline_id`, `first_stage_id`, `nodes` and `edges`.
- It shows one question per screen.
- Node types seen: `start`, `question`, `end` (with `subtype: "success"`).
- Answer types seen: `short_text`, `long_text`, `mcq` (one choice).
- `contact_field` values seen: `name`, `email`, `phone`.
- Branching is on edges: `condition_value` is the chosen option's id and `condition_label` is its text. An edge with neither always applies.
- No multiple-choice (pick several) type, "required" setting or help text appeared in the data.

The specs use only these features, so they should need no new question types. If the app has a pick-several type, the specs mark where it would be better.

## Rules for every form

**Wording.** Use the question text, options and messages in the specs as written. They are public-facing and have been matched to the website.

**Contact fields.** Map name, email and phone to `contact_field`, as the founder form does, so the app creates or matches a contact.

**Existing contacts.** If the email already belongs to a contact, attach the submission to that contact. The same person may submit more than one form: keep every submission.

**Validation.**
- Email: must be a valid address.
- Phone: accept international numbers with a country code, since NRI and UAE applicants are expected. Do not force 10 digits.
- LinkedIn: accept with or without `https://`. "None" is a valid answer.
- Every question is required unless the spec says optional.

**Never ask for** PAN, Aadhaar, passport, bank or demat details, net worth proof or document uploads. KYC happens later, in person. This also applies to any question added later.

**No deal information.** The forms must not show, name or link to live deals, deal terms or returns, including on the success screen and in emails. The pages are public.

**Consent.** The consent question is a required step and must be the last question. Store the answer with the submission time and the exact wording shown. Link the words "privacy policy" to the app's existing privacy page. If there is none, stop and ask (see Questions).

**Source.** Record on each submission that it came from the website, using the app's existing link or source field. The links above carry no query string. No tracking parameter is needed (confirmed).

**Notifications.** Follow what the founder form does on submission. If it does nothing, stop and ask who should be told.

**Spam.** Use whatever protection the founder form has.

**Design.** Same template as the founder form: logo, progress, buttons, T&C link.

## Done when

- [ ] Each link opens signed out, on desktop and phone, with no login redirect.
- [ ] Every question, option and branch matches the spec, in order.
- [ ] Each branch has been walked through to the success screen.
- [ ] A test submission of each form appears in the right pipeline, at the first stage, with name, email and phone on the contact. Remove the test data afterwards.
- [ ] Submitting two forms with one email leaves one contact with two submissions.
- [ ] Required questions, and a bad email address, block the Next button with a clear message.
- [ ] The form works with the keyboard alone.
- [ ] `/apply` (the founder form) and the published forms behave exactly as before.

## Send back

1. The final public link for each form, if it differs from the table above.
2. Anything built differently from the spec, and why.

The website's buttons already point at the links in the table, so the forms must be live at those paths before the page is published. If a link has to differ, tell us and we will change it on the website. **Do not edit the website repo from the ecosystem side.**

## Questions for Earlyseed Ventures

Ask these if the codebase does not answer them:

1. Who is notified of each submission, and who owns each pipeline?
2. Which privacy policy and terms pages should the forms link to?
3. Should applicants get a confirmation email? If so, from which address?
4. Are SGPs and franchise partners the same programme in the CRM?
