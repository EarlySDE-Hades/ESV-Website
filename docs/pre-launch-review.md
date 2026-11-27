# Before we go live: review list

Internal. Work through this before the site moves to `www.earlyseedventures.com`. Nothing in `docs/` is published.

Tick an item when it is done. Add new ones under the heading that fits. "Must" means don't go live without it.

## Must: legal and privacy

- [ ] Rahul reviews the risk notice on the Invest page, and the consent wording on all four forms.
- [ ] **Privacy policy and terms.** The forms have a privacy policy, but the website's footer links to neither. Decide whether the site links to the same pages.
- [ ] Rahul confirms the Invest page wording works for a public page (syndicate from ₹5 Lakh, partner descriptions).
- [ ] The About page's goal, "Launch a ₹100 Cr Category I AIF" (2027): can it be public before registration?
- [ ] Consent from the angel investor quoted on the About page.
- [x] Guests in the event photos are happy to be shown (confirmed 25 Nov 2026).
- [x] People in the Careers photos are happy to be shown (confirmed 25 Nov 2026).

## Must: forms

- [ ] Send a test through each form (founder, syndicate, partner, intern): it reaches the right pipeline, the right person is told, and the privacy policy link works. Remove the test data.
- [ ] Intern form: the HR task reaches Dhwani Joshi, due in 2 weeks. "No" to 18 or older stores nothing.
- [ ] Who is notified of syndicate and partner applications, and who owns each pipeline?
- [ ] Job form (`/apply/careers`): build it when there is a role to fill. Spec: `docs/ecosystem-forms/job-form.md`.

## Must: placeholders a visitor can see

- [ ] **Team page, Advisors:** five grey placeholder cards and "will be announced soon". Add the advisors or hide the section.
- [ ] **Events page, Upcoming:** two "To be announced" rows with disabled Register buttons (investor session, campus programme). Fill in or remove.
- [ ] Events page headline and intro were written as placeholders: approve or change.
- [ ] Perspectives: Podcasts has no episodes yet. Keep, or hide until there are some.
- [ ] Prologue: Founders' Bootcamp is marked "Coming soon". Still right?

## Must: moving the domain

- [ ] Point the domain at Vercel. Every page already names `www.earlyseedventures.com` as its address.
- [ ] Redirect the old site's addresses so links and search results keep working:
  `/about`, `/services`, `/copy-of-services`, `/copy-of-founder`, `/portfoliogeneral`, `/portfoliosyndicate`, `/education`, `/impact`, `/connectwithus`, `/contact`, `/team`. There may be more: check the old sitemap. There is no `vercel.json` yet.
- [ ] Email on the domain (`info@`) keeps working after the change. Check the mail records before touching DNS.
- [ ] Submit the new sitemap in Google Search Console.
- [ ] Add a 404 page in the site's design. There is none.
- [ ] Decide on analytics. There is none today. If added, update the privacy policy first.
- [ ] Check the link preview (title, image) on WhatsApp and LinkedIn.

## Events

- [ ] Rotary for Business: exact date. The site says "March 2026" (post of 23 Mar 2026).
- [ ] International Investors Summit, Dubai: exact date. The site says "Early 2026" (post of 7 Feb 2026).
- [ ] BNI Global Convention: photos, to replace the announcement graphic. The team will provide them.
- [ ] The Startup Mixer, Edition 2: the page uses the press release of 31 Aug 2026, written before the event. Confirm it ran as announced (2 Sept 2026, NESCO, Goregaon; Agnelo Rajesh Athaide, Manan Patel, Rahul Hingmire). Is naming Agnelo Rajesh Athaide as host fine?
- [ ] The Startup Mixer, Editions 3 and 4: dates and details. Photos of Editions 1 to 4. The team will provide them.
- [ ] The Startup Mixer, Edition 5 (2 Dec 2026): the poster for Nimit came twice. Is there a third speaker? After the event, add a recap.
- [ ] The Startup Mixer: the first edition's poster, the Edition 2 press release and the Edition 5 Luma page all call us a supporter, and the site says co-host. Agreed with the other hosts?
- [ ] The Startup Mixer, Edition 5: the poster says ₹1,500, and the Luma page lists registration as free, with approval. Which is right?
- [ ] Photos for Bihar StartUp Showcase, The Startup Mixer (Edition 1) and the AIC-RRU session, which use posters.
- [ ] Dates taken from outside the posts: IFTA (10 Dec 2025), GITEX (13 to 17 Oct 2025), BNI (28 to 30 Oct 2026). Confirm.
- [ ] Dubai summit: Flip, SICI and Anahad pitched, and the post calls them portfolio companies, but they are not on our Portfolio page. Add them?
- [ ] Event posts name only our co-founders, Flying Wedge's founder and the Dubai summit's organiser. Keep it that way?

## Careers

- [ ] Open roles, or confirm "We have no full-time roles open right now".
- [ ] Internships: are the four teams and their descriptions right? Any fixed duration, stipend or location?
- [ ] Should the Careers page say interns must be 18 or over? The form stops under-18s at question 4.
- [ ] Dhwani Joshi's title: the site says "Bootcamp Coordinator", and she is also HR.
- [ ] Dates of the team stories: 2025 (Model UN, art workshop), October 2025 (ideas), December 2025 (massages), September 2026 (women and money).
- [ ] Original photos for `mun-debate`, `mun-room`, `wellness` and `money-session`, or the Codex versions (`docs/archive/codex-careers-photos.md`).

## Company profiles

- [ ] **Founder photos still needed** (initials until then): The Artment (Aditya Agarwal, Aanchal Agarwal), WinMagic Toys (Mukesh Jagwani), EsportsXO (Utsav Umang, Rohit Raj, Vikas Goel), Regenerix (Aanchal Jain), Kalaneca (Ramya Rao, Kavea Chavali).
- [ ] **Larger founder photos would be sharper** (200px today): Hesa (both), OLL, Flying Wedge, Skyroot (Bharath Daka), Alchemyst AI (both), Cup-Ji (Jay Sotta), JustDeliveries.
- [x] Founder photos from LinkedIn and other sites are fine to be public (confirmed 25 Nov 2026).
  Put each in `Founder Photos/companies/<company slug>/<first-last>.jpg`, run `python tools/portfolio/assets.py`, then `python tools/build.py`.
- [x] People shown for Kyoora, JimzCart, Shaurrya and Misfits are fine to be public (confirmed 25 Nov 2026).
- [ ] Shaurrya: we show Sudeb Sarbadhikary (Founder and Director, Finance) and Pankaj Agrawal (Chairman), as in their deck. Add anyone else, such as Mahesh Choudhary?
- [ ] Cup-Ji: Jay Sotta and Aakash Sotta are from press coverage of Shark Tank India. Confirm.
- [x] Frevolt founders added from their deck of 19 Oct 2026 (Sanket Vyavahare, Ashutosh Bhavsar, Pooja Shetty).
- [ ] Logos needed: DCGpac and WinMagic Toys (current versions; our deck has older ones). A larger JimzCart and ElectriQ logo would be sharper. JimzCart's own deck uses a newer gold logo: which is current?

## Invest page

- [ ] Strategic Growth Partner copy and the four steps, including "Orientation", were drafted by us. Approve.
- [ ] Are Strategic Growth Partners and franchise partners the same programme?
- [ ] The deck's current raises start at ₹25 Lakh, and the syndicate minimum is ₹5 Lakh. Which should people see?

## Company facts

- [ ] Founding year: the About page says 2020 (as regional partners) and 2022 (incorporated). Agree on one for general use.
- [ ] Headline numbers: 400+ HNIs and family offices, 300+ venture funds, 4,000+ students. Still right?
- [ ] "Ms." before Monica Gupta's name in her profile, when others use "CA": keep or drop?
- [ ] Home page: the campus partner summaries and the portfolio summaries were written from each organisation's website. Review them.
- [ ] Image rights for the remaining event and campus photos.
- [ ] Any image the About page still needs.

## Housekeeping

- [ ] `index.html` is served as written, so its code comments are public. They hold no sensitive notes today; check again before launch. Comments are removed from every other page when it is built.
- [ ] `README.md` is out of date: it says there is no build step, and lists a font we no longer use.
- [ ] Final pass on a real iPhone and Android phone, and with a keyboard only.

## Founder stories (Perspectives)

- [ ] Rahul reviews the Hesa story's line that our investment "returned more than five times its value" (from the bootcamp deck of 7 Aug 2025). A past return on a public page may need a disclaimer, or a softer line.
- [ ] Hesa and OLL founders are happy with their stories. The facts come from the bootcamp deck and their profiles. The "What founders can take from it" lessons are our own.
- [ ] OLL: the deck dates the Shark Tank deal to 2022, and the profile says Season 2 (aired 2023). The story gives the season, not the year.

## Tools

- [ ] Rahul reviews the tools' wording and the "not financial, legal or tax advice" note, especially before the investor tools (return calculator, pro-rata cost) go live.
- [ ] Round finder ranges are the middle half of disclosed Indian rounds, October 2025 to September 2026 (Tracxn), from the Prologue article. Refresh them once a year.
- [ ] Phase 2: exit waterfall, ESOP pool sizer and vesting schedule. Phase 3: investor tools, iSAFE converter, raise-ready checklist. They show as "Coming soon" on tools.html until built.
