**Blue Buoy — Help Us Build the New System**

We're starting to plan a replacement for our FileMaker system — scheduling, billing, attendance, all of it. Before anyone builds anything, we need to understand how the business *actually* works day to day.

| Please don't try to answer all of this at once. There are a lot of questions here — that's on purpose, so nothing gets forgotten. Skim it, answer whatever's easy, skip anything that doesn't apply to you, and flag the ones that need more thought. Even a few answers help. |
| :---- |

**How to use this document**

* **Type your answers directly under each question.** No need to make it neat — bullet points, half sentences, whatever is fastest.

* There are no wrong answers. Saying we just do it by hand, or that we gave up on something years ago, gives us some of the most useful information there is.

* We've studied what the *software* does. What we can't see is what *you* do — the workarounds, the things kept on paper or in your head, the stuff the system never handled.

* **Different people will know different things.** Some questions are billing, some are scheduling, some are pool deck. Answer the ones in your world and leave the rest.

* If you only have time for one section, jump to **Part 2**. It's worth more than all the rest combined.

**Where to start**

There are a lot of questions here. If you only get to a few things, these are the ones that would help most:

* **The Monthly Billing Run** — the month-end process, how long it takes, and what goes wrong. This is the biggest thing we want to fix.

* **Charter Schools & Regional Center** — none of this lives in the software today, so we know almost nothing about it.

* **Part 2** — what takes way longer than it should, and what you do outside the system entirely.

| Rough answers are fine. "About half a day," "maybe a dozen families," "it happens sometimes" — estimates are genuinely useful. Don't go looking things up unless you want to. |
| :---- |

| Part 1: The Big Open Questions |
| :---- |

These came up during the analysis and genuinely can't be answered from the software alone.

## **Pricing & Discounts**

**1\.  The sibling discount** currently works like this: 1st lesson slot in a household is full price, 2nd gets one discount step, 3rd gets two steps, and the 4th and beyond all get three steps (the discount stops growing after the 4th). **Is that still the intended policy?** It's hard-coded with no explanation anywhere, so it may be stale.

*Answer:* 

**2\.  How often do you set up special one-off pricing** for a family (like the private-at-semi-private-rate arrangement we saw)? A few times a year, or regularly? That determines how much we invest in making that easy vs. just possible.

*Answer:* 

**3\.  When you raise prices**, what's the process today? What's annoying about it? (We know prices change once a year at the start of the new year, and that prepaid families need a manual adjustment every month afterward — what else is involved?)

*Answer:* 

## **Charter Schools & Regional Center (biggest gap — most important section)**

We found that the system lists 14 charter schools and 9 Regional Center agencies as billing options, but only as a text note telling staff how to bill. Everything after that appears to happen manually. These questions matter a lot, because this is probably the largest thing the new system could take off your plate.

**4\.  Walk us through billing a charter school**, start to finish. How do you know what to bill, what do you send them, in what format, and how do you know when they've paid?

*Answer:* 

**5\.  Where does that information live today?** A spreadsheet, a separate program, paper, email? (There's no trace of it in the FileMaker system.)

*Answer:* 

**6\.  Do charter schools authorize a set number of lessons or a dollar amount** up front — like a purchase order with limits and an expiration? If so, how do you currently track how much is left?

*Answer:* 

**7\.  Has a student ever kept taking lessons past what a school or agency authorized**, leaving you unpaid? How did you find out?

*Answer:* 

**8\.  How long do they typically take to pay**, and how do you track what's overdue?

*Answer:* 

**9\.  Is Regional Center billing different from charter school billing?** Different forms, different timing, different documentation?

*Answer:* 

**10\.  Do institutional payers always pay full price**, or are there negotiated rates per school/agency?

*Answer:* 

**11\.  Can one family have different payers for different kids** — e.g. one child through a charter school and a sibling paid by the family?

*Answer:* 

**12\.  What documentation do they require** to release payment — attendance sheets, signed service logs, progress notes?

*Answer:* 

**13\.  What's the most frustrating part of this whole process?**

*Answer:* 

## **Payment Plans & Prepay**

**14\.  What prepay options do you actually offer?** The system has discount tiers of 5%, 10%, 15%, 20%, 25%, 50%, and 100% — which are really in use, and what determines which one a family gets?

*Answer:* 

**15\.  The prepay-before-the-price-increase offer** — how long does that locked rate last? The whole next year? Until the prepaid lessons run out? Something else?

*Answer:* 

**16\.  The monthly adjustments for prepaid families** — roughly how many families are you doing this for, and how long does it take each month? (We now understand the system applies the new rate anyway and you manually back out the difference each month. This is near the top of the list to eliminate.)

*Answer:* 

**17\.  Has a month ever gotten missed**, or an adjustment entered wrong? How did you catch it?

*Answer:* 

**18\.  What happens if a family prepays at the old rate and then quits partway through?** Refund at which rate, and how is that figured today?

*Answer:* 

**19\.  Can a family prepay for part of a year** (say six months)? If so, what happens when it runs out — do they move to the new rate then?

*Answer:* 

**20\.  Besides prepay differences, what else do you use adjustments for?** (Courtesy credits, billing corrections, something else?) We want to keep adjustments available for real one-offs while removing the ones the system should just handle.

*Answer:* 

**21\.  What's the difference between the plan types** in practice — monthly auto-charge vs. prepay vs. card-on-file? Do families move between them?

*Answer:* 

**22\.  The system only allows two payments per month per family.** Is that ever a problem?

*Answer:* 

**23\.  How do you handle gift certificates, referral credits, and account credits** currently? Do they work well?

*Answer:* 

## **The Monthly Billing Run (highest priority — this is where the most time goes)**

Here's what we understand about the month-end process today. **Please correct anything wrong and fill in the gaps** — this is the area we most want to fix, and rough time estimates are genuinely useful.

Our current understanding of the steps:

* Manually post each family's lesson type for the month

* Manually work out prorated amounts for partial months

* Cross-reference a spreadsheet from the credit card company against what's being charged

* Manually reset families who had referral credits back to their normal fee the next month

* Void or refund families who cancel after billing has processed (roughly a one-week window)

**24\.  Is that right, and what did we miss?**

*Answer:* 

**25\.  Roughly how long does the whole month-end process take you?** Even a rough number ("most of a day," "two evenings") helps make the case for fixing it.

*Answer:* 

**26\.  Which step is the worst?** The one you dread, or that causes the most re-work.

*Answer:* 

**27\.  How many families typically need a prorated amount** in a given month?

*Answer:* 

**28\.  How many need a referral credit reset?**

*Answer:* 

**29\.  Has a referral credit reset ever been missed?** How did you find out? (This one worries us — a missed reset means a family keeps getting discounted with nothing flagging it.)

*Answer:* 

**30\.  How often does the credit card cross-reference turn up a mismatch**, and what do you do when it does?

*Answer:* 

**31\.  When a student changes lesson type mid-month**, how do you decide what to charge — the old rate, the new rate, or split between them? Is there a consistent rule?

*Answer:* 

**32\.  How often does the office forget to tell you about a mid-month change?** (You mentioned this happens — no blame intended, we want the system to carry that instead of a person.)

*Answer:* 

**33\.  What's the actual void/refund window**, and who decides whether to void versus refund?

*Answer:* 

**34\.  What else goes wrong during billing** that we haven't asked about?

*Answer:* 

## **Payment Processing**

We believe the setup is Affinity24 (Tustin) as the processor, Authorize.Net as the gateway, settling to Wells Fargo. A few things that affect a real decision about keeping it:

**35\.  Is that right?** Anything else in the mix?

*Answer:* 

**36\.  Roughly what's the monthly credit card volume?** (Not counting charter school / Regional Center payments, which come by check.)

*Answer:* *(Round 2 Q17, answered 2026-09-10)* This is about how many students/families we process per month [the earlier "550–700"]. Monthly credit card volume ranges from ~$156,000–207,000. Charter schools that pay by direct deposit or check have increased in volume to ~15% of income. Estimated 2026 total gross income: $2,650,000.

**37\.  Do you know your effective processing rate?** It's usually on the monthly statement.

*Answer:* 

**38\.  Do you have a rep at Affinity24 you actually call**, and are they helpful?

*Answer:* 

**39\.  Do cards on file ever expire and cause a failed payment?** How do you handle it currently? (Authorize.Net has an automatic card-updating service that may not be turned on.)

*Answer:* 

**40\.  How do failed payments get noticed and followed up today?**

*Answer:* 

## **Closures & the Holiday Break**

**41\.  During the two-week December/January closure**, families still pay their normal monthly amount — no credit or reduced bill, correct?

*Answer:* 

**42\.  Do families ever push back on that**, and how do you handle it when they do?

*Answer:* 

**43\.  For one-off closures** (a holiday, weather, pool maintenance) — does everyone affected automatically get a make-up credit? Always, or are there exceptions?

*Answer:* 

**44\.  How do you close the pool for a day** and get make-ups issued to everyone today? How long does that take?

*Answer:* 

**45\.  Is there a master list of closure dates** for the year anywhere, or is it handled as each one comes up?

*Answer:* 

## **Make-Ups & Cancellations**

**46\.  Is there a cutoff for late cancellations** where a family loses their make-up credit — same-day, 24 hours, etc.? Or is it always a judgment call? Should it become an automatic rule, or do you want to keep discretion?

*Answer:* 

**47\.  Should make-up credits expire?** We found one student with 28 unused private-lesson credits banked. Is that normal? Is it a problem?

*Answer:* 

**48\.  When do you decide NOT to issue a make-up?** What situations?

*Answer:* 

## **Billing**

**49\.  Is the family or the individual student the "real" account** when it comes to who owes what? The current system tracks both at once and it's ambiguous which one wins.

*Answer:* 

**50\.  How do you handle a family with a past-due balance?** Is there a point where lessons stop? Who decides?

*Answer:* 

**51\.  What billing situations does the system NOT handle**, so you deal with them manually or outside the system?

*Answer:* 

## **Waitlist & Scheduling**

**52\.  How do you currently match waitlisted kids to open slots?** Walk through what you actually do — that helps us automate the right thing rather than a guess.

*Answer:* 

**53\.  How often do parents turn out to be more available than what they originally told you?** (We're planning to show all matching openings, not just their stated window — want to confirm that's useful.)

*Answer:* 

**54\.  What makes a match a bad idea even when it looks fine on paper?** (Teacher/student chemistry, sibling logistics, etc.) These stay human decisions — we just want to know what to surface so you can judge quickly.

*Answer:* 

## **Searching (important — please don't skip)**

We saw the Deck Manager search screen and it's genuinely powerful. The biggest way a project like this goes wrong is replacing a capable search with a prettier but weaker one, so we want to get this right.

**55\.  What searches do you run most often?** Even the boring everyday ones — those become one-click buttons in the new system.

*Answer:* 

**56\.  Do you use Saved Finds?** If so, which ones?

*Answer:* 

**57\.  What's the most complicated search you've ever needed to build?** (Multiple criteria, excluding certain students, etc.)

*Answer:* 

**58\.  Is there something you've wanted to search for and couldn't?**

*Answer:* 

**59\.  Do group lessons work differently** from private/semi-private in ways we should know about — scheduling, pricing, make-ups?

*Answer:* *(Round 2 Q1–Q5, answered 2026-09-10)* **Minimum:** we keep the class open as group whether there is 1 student or none. The only exception is if the class is completely open for the day and we need a sub for another teacher — we will use the class for other options (SP, PR, M SP, M PR, or PM). **Price:** stays the same regardless of how many students. **Sibling discount:** we usually try to use the group class as the first lesson; that way the more expensive classes get the discounted prices. **Make-ups:** group make-ups (GR, ST, PM) can be used either as their lesson type or, if the family has more than one group make-up, converted: 2 = 1 Semi-Private make-up, 4 = 1 Private make-up. **Joining:** there are set times for all the different group classes we offer; that schedule typically stays the same year after year. To join Stroke Tech or Stroke Prep the student must meet the age and swim-level requirement.

## **Class Types & Eligibility**

We have approximate requirements but need them confirmed exactly, since the system will enforce them.

**60\.  What are the exact requirements for each class type?** Our current understanding (likely imprecise): Parent & Me is age 3 and under; Group needs age 7+ and level 8+; Stroke Tech needs age 10+ and level 10+. Please correct.

*Answer:* *(Round 2 Q5, answered 2026-09-10)* Stroke Prep (Group): ages 7 and older, swim level 9–12. Stroke Tech: ages 10 and older, swim level 10–12. Parent & Me: no level requirement, ages 0–3. *[Transcription note: the Deck Manager screenshot returned with Round 2 shows one Group class banded `AGE 7+ lv 8/9/10` next to one banded `AGE 7+ lv 9-10`, so bands are set per class and at least one admits level 8. Keep the bar per class, not per type.]*

**61\.  Are there requirements for the other types** — Private, Semi-Private, Adult — or can anyone take those?

*Answer:* *(Round 2 Q6, answered 2026-09-10 — Adult only; Private and Semi-Private still unanswered)* The Adult class is a group class; I believe it can have up to 6 in a class, age 16 or older. Payment is set up differently: they can pay for a single class, a package of 4, or a package of 8 lessons. We only take a lesson from their account if they show for a class (based on the teacher's roll for the day). However, we run into a problem that the adult doesn't notify us if they will be out. We need to look into a way to improve on this.

**62\.  Is it always age AND level**, or does one sometimes substitute for the other? (E.g. a strong 6-year-old at level 9 — could they join Group?)

*Answer:* 

**63\.  How often do you make exceptions**, and who decides?

*Answer:* 

**64\.  What happens when a child ages out of Parent & Me?** Is that tracked, or do you catch it as it comes up?

*Answer:* 

**65\.  Would it help to see students who are one level away** from qualifying for Group or Stroke Tech? (Could be useful for parent conversations and keeping kids progressing.)

*Answer:* 

**66\.  Are there other class types** we haven't seen — seasonal programs, clinics, camps, private groups?

*Answer:* 

**67\.  Are there other color highlights or visual cues** on your screens that mean something important? (We found the under-4 age highlight signals the swim diaper requirement — there are likely others we'd otherwise miss, since they don't show up anywhere in the database itself.)

*Answer:* 

**68\.  Are there other ways you encode meaning by how you type something?** We know about ALL CAPS first names (special needs students, and difficult parents). Others might include: bold text, abbreviations in notes, a symbol or punctuation added to a name, putting something in a particular field that isn't quite what that field is for.

*Answer:* 

**69\.  What do the common note abbreviations mean?** We've seen things like "AUG PO," "WORK," "MU," "OUT" — a quick glossary of the shorthand your team uses would help a lot.

*Answer:* 

**70\.  Are there other pool rules or requirements** tied to age, level, or student status that staff just know — things a new instructor would have to be told?

*Answer:* 

**71\.  For the ALL-CAPS parent convention** — is that something you'd want carried into the new system, or handled differently? (Our suggestion: a proper account note with a reason and a date, visible only to office staff, rather than changing the person's name. Happy to do it either way — your call.)

*Answer:* 

## **Communication**

**72\.  What do you use the bulk texting for most often?** Sub notices, closures, reminders, something else?

*Answer:* 

**73\.  What do you wish you could send but currently can't** — or that's too tedious to bother with?

*Answer:* 

**74\.  Do families ever reply to those texts?** If so, where do the replies go and who handles them?

*Answer:* 

## **Notes & Student Information**

**75\.  What kinds of things end up in the instructor notes?** (We know: allergies, special needs, past experiences/fears. Anything else?)

*Answer:* 

**76\.  Should a serious allergy look different from a general note?** Right now everything is "there's a note, tap to read." For something potentially urgent, would you want it more prominent — or does the current approach work fine?

*Answer:* 

**77\.  Who enters these notes today** — office staff from what parents tell them, or do instructors add their own too?

*Answer:* 

**78\.  Should instructors be able to add their own observations** about a student's progress, separate from what parents provided?

*Answer:* 

**79\.  How does this information get collected initially** — a paper form at signup, a conversation, over time?

*Answer:* 

## **Access & Permissions**

**80\.  Who should be able to do what?** Specifically: should desk staff be able to change prices? Issue make-ups? See other families' billing?

*Answer:* 

**81\.  Has anything ever been deleted or changed by accident** that was hard to recover? (We already know about the record-deletion incident — wondering if there are others.)

*Answer:* 

**82\.  Right now the instructor iPads have no real login** — the password prompt can be cancelled and it opens anyway. Has that ever caused a problem, or is it just how it's always been? Any concern about an iPad walking off with student info on it?

*Answer:* 

**83\.  Would a short PIN at the start of a shift be acceptable**, if switching between teachers' schedules stayed instant and password-free? (We want to keep the grab-any-iPad convenience — just add a light barrier at the start.)

*Answer:* 

**84\.  Does it matter who marked attendance?** Right now if you take your roll on a colleague's iPad, there's no record of who actually entered it. Worth tracking quietly in the background, or genuinely doesn't matter? (Either way, it won't add a step to your workflow.)

*Answer:* 

**85\.  How often does the dead-battery handoff happen** — grabbing another iPad late in the day to take your roll? Daily, occasionally? (It affects how much we cache on each device for offline use.)

*Answer:* 

**86\.  Do you ever need to take roll somewhere with no WiFi**, or is coverage solid across the whole pool deck?

*Answer:* 

## **Remote Access & Staff Turnover**

**87\.  When someone leaves, what happens to their access today?** Does anyone change passwords, or does it generally stay as-is?

*Answer:* 

**88\.  How many people share the same login?** (We noticed a saved "deck manager" password — wondering how widely shared logins are used.)

*Answer:* 

**89\.  Who needs access from off-site**, and for what? (You, your wife, scheduling office staff — do instructors ever need it from home?)

*Answer:* 

**90\.  Would a log of who accessed what be useful to you**, or is that more than you'd ever look at?

*Answer:* 

**91\.  Has there ever been a concern about a former employee** still having access, or taking family/student information with them?

*Answer:* 

**92\.  Who currently manages your FileMaker server** — someone in-house, or an outside consultant? (Relevant for the unencrypted-connection issue, which is worth fixing now regardless of this project.)

*Answer:* 

## **Backups & Recovery**

**93\.  What backups exist on the current system**, and has anyone ever actually restored from one? (Worth confirming — an untested backup isn't really a backup.)

*Answer:* 

**94\.  When that family record got deleted, what did you do?** Was anything recoverable, or was it re-entered from scratch?

*Answer:* 

**95\.  How long could you operate if the system were down** — an hour, a day? That tells us how fast recovery needs to be.

*Answer:* 

## **Devices**

**96\.  What does each person actually work on?** (Desk staff — desktop or laptop? Do you or your wife work from a phone often, or mostly laptop?)

*Answer:* 

**97\.  Is there anything you'd want to do from your phone** that you currently can't?

*Answer:* 

**98\.  Do the scheduling office computers have any constraints** — old machines, small screens, a specific browser?

*Answer:* 

## **Follow-ups (added September 2026)**

New questions that surfaced after the original set went out.

**Round 2 (answered 2026-09-10).** A second, separately numbered document — [`docs/migration/BlueBuoy_Round2_Questions.docx.md`](./docs/migration/BlueBuoy_Round2_Questions.docx.md), Round 2 Q1–Q20 — came back answered out of band. Its answers are transcribed here under the `qa.md` question they answer, each citing "Round 2 Qn"; questions it asked that had no `qa.md` counterpart are added below as Q103–Q108.

**99\.  Which FileMaker file is the live one — `BlueBuoy_FM` or `BlueBuoy_FM_2024`?** Both exist on the server; we analyzed `BlueBuoy_FM` and need to know whether that's the one in daily use. (For whoever manages the FileMaker server.)

*Answer:* *(Round 2 Q18, answered 2026-09-10)* We use `BlueBuoy_FM` currently. `FM_2024` is a history file. What happens is our system slows due to too many files, so we archive families that have not been enrolled for 10 years. We still need access to the old files (rarely) but need to see, just in case a family returns years later.

**100\.  Make-up credit conversion between lesson types** — we heard credits can be traded across types (something like a few group credits equaling one semi-private, and about four group equaling one private). Is that right? What are the actual ratios, which directions are allowed (can a private credit be split into group credits?), and does someone approve each conversion or is it automatic?

*Answer:* *(Round 2 Q7–Q11, answered 2026-09-10)* Yes. 2 Semi-Private make-ups = 1 Private make-up; 1 Private make-up = 2 Semi-Private make-ups; 2 Group (ST, GR, PM) = 1 Semi-Private make-up; 4 Group (ST, GR, PM) = 1 Private make-up; 1 Private make-up = 4 Group make-ups. **Which conversions are allowed** (group → semi-private, group → private, semi-private → private): yes. **Reverse** (a private credit split into several group credits): yes. **Who decides:** when scheduling the make-up we choose which option we want to use. However, when moving make-ups between siblings we note how many make-ups and what type were moved from one child to the other. **Existing private credits when a student switches to group:** they stay as Private make-ups and can be used as either Private or converted to other make-up options.

**101\.  The military discount** — how much is it, and does it stack with the sibling and prepay discounts?

*Answer:* *(Round 2 Q16, answered 2026-09-10)* Yes, we offer an additional 10% discount for first responders (military, police, and fire department). We ask them to provide ID to verify; I would like an option to flag whether this has been provided. Yes, the discount stacks on both the sibling and prepay discounts.

**102\.  When you offer a family a make-up slot, how long should they get to answer** before the offer moves on to the next family? Today this is informal — we want to put a real clock on it, so tell us what feels right (a few hours, a day, ...).

*Answer:* 

**103\.  What reports do you run regularly?** Weekly, monthly, whenever — even the boring ones. *(Round 2 Q12)*

*Answer:* *(Round 2 Q12, answered 2026-09-10)* **Daily:** weekly enrollment by lesson type vs the same period in previous year(s). The search for student enrollment for each weekly period / lesson type (less make-up lessons or sub for teacher) is done manually and entered manually into an Excel spreadsheet. Representative rows (columns SP · PRI · PM · ST · GR · AD · TOTAL · week · prior-year total · increase): 790 · 155 · 127 · 8 · 34 · 2 · 1116 · <1/1/26 · 1056 · 60; 698 · 142 · 121 · 7 · 29 · 3 · 1000 · <1/4/26 · 938 · 62; 769 · 151 · 123 · 7 · 34 · 3 · 1087 · <1/11/26 · 1030 · 57; 778 · 150 · 126 · 8 · 34 · 3 · 1099 · <1/18/26 · 997 · 102; 764 · 149 · 135 · 8 · 34 · 3 · 1093 · <1/25/26 · 1049 · 44; 805 · 155 · 134 · 8 · 36 · 3 · 1141 · <2/1/26 · 1073 · 68; 808 · 150 · 135 · 9 · 33 · 3 · 1138 · <2/8/26 · 1071 · 67; 818 · 154 · 135 · 9 · 33 · 3 · 1152 · <2/15/26 · 1079 · 73; 807 · 150 · 130 · 9 · 33 · 3 · 1132 · <2/22/26 · 1061 · 71. **Daily:** reports on free trials or make-up trials that came in the day before — we call the families to follow up and see if they would like to enroll in the times tried, or if the teacher did not think it was a good match, or if the time did not work, to find a new opening. Notes from the pool deck or teachers about any lesson changes, requests, or impromptu make-ups scheduled after our scheduling office closed. [Screenshot 1: the four report buttons.] **Weekly/monthly:** a waitlist report of open requests, to check on spots that might have opened on the schedule board — we hope this can be eliminated and set up automatically. **Monthly:** a search for enrolled students' prepays that will be ending in the current month and still have open enrollment going into next month; we send reminders via text and email about prepaying again, or their account changes to auto-billing starting the 1st. **Monthly:** a search for currently enrolled students to check that their monthly tuition payment matches the Authorize.Net batch that will process on the 1st of the new month. **Daily / week of:** when looking for make-ups for the day, a button on top of our schedule board finds students that have reported an absence. [Screenshot 2: the `Search Out` button.]

**104\.  Does anything get printed or exported** — to your accountant, to charter schools, to Regional Center? *(Round 2 Q13)*

*Answer:* *(Round 2 Q13, answered 2026-09-10)* QuickBooks General Ledger, P&L, and Balance Sheet are exported to the accountant for the previous calendar year in Jan/Feb for preparation of tax returns. Jen keeps an Excel spreadsheet for students with Regional Center payments, so we can keep track of what is behind and what has been paid. [Screenshot 3: that spreadsheet.]

**105\.  Is there a report you rely on that would be painful to lose?** *(Round 2 Q14)*

*Answer:* *(Round 2 Q14, answered 2026-09-10)* Looking for absences — this is really a scheduling feature instead of a report, but we still need it; we use it all day. Reports on free trials / make-up trials, notes from deck and instructors. Also the attendance sheet on each student's account. [Screenshot 4: a student's attendance layout.]

**106\.  Is there a report you wish existed** but doesn't? *(Round 2 Q15)*

*Answer:* *(Round 2 Q15, answered 2026-09-10)* A quick summary of monthly tuition for students on our auto-pay. A report of students that have not shown for more than 2 weeks without notice. Changes of lesson type for ongoing enrollment — for example a change from Parent & Me to Semi-Private, which changes billing — so we can make adjustments to either the prepay or the monthly rate.

**107\.  How is a substitute found today** when a teacher calls out? Walk us through it. *(Round 2 Q19)*

*Answer:* *(Round 2 Q19, answered 2026-09-10)* We look at the schedule of the teacher who is out and cross-reference other teachers who work during that time to see what openings they have: an open spot, a student out, or a student starting the week after (making the current day available). Sometimes we need to be aware that the student has special requests — female-only teachers, to be paired higher or lower, or a sibling enrolled around that time, in which case we want a spot either at the same time or right after for the student who needs the sub. When we can't find anything we look around that time, or at the student's availability from previous requests, to see what we can offer if they have flexibility for the day. When all else fails we have an on-call teacher take the lessons we could not fill.

**108\.  Has a lesson ever been scheduled during someone's lifeguard shift** by mistake? (Our system won't know about guard shifts — those only live in Humanity.) *(Round 2 Q20)*

*Answer:* *(Round 2 Q20, answered 2026-09-10)* Only if we have to switch them from guarding to subbing for the day.

| Part 2: The Most Important Question |
| :---- |

**What takes way longer than it should?**

*Answer:* 

And its companion: **what do you do outside the system entirely** — on paper, in a spreadsheet, in your head, in a text thread — because the software can't handle it?

Please be specific and don't self-edit. "I have to check three different screens to answer one parent's question" is exactly the kind of thing worth fixing, and exactly the kind of thing that never shows up in a software analysis.

Also worth knowing: **what do you actually like about the current system?** We don't want to accidentally throw away something that works well just because it's old.

| Part 3: Ideas We Haven't Built Yet — What Sounds Useful? |
| :---- |

These are all *possible* with the data you already have, but the current system was never built to do them. We're not committing to any of these — just want to know which sound genuinely useful versus which would be noise.

Rate them however you like: "yes please," "nice but not important," or "we'd never use that."

| Idea | What it would do |
| :---- | :---- |
| **Attrition warnings** | Flag families who look like they're drifting away — attendance dropping off, end date approaching with no renewal — *before* they quietly disappear |
| **Level progression tracking** | Show which students have been stuck at the same level for a long time (e.g. "14 students at Level 5 for 6+ months") — useful for teaching quality and for parent conversations |
| **Instructor utilization reports** | Who's consistently full, who has open capacity, trends over time — helps with hiring and scheduling decisions |
| **Revenue forecasting** | Project next month's expected revenue from current enrollment, and flag the gap between expected and actually collected |
| **Family self-service portal** | Parents could view their own schedule, balance, and make-up credits online — without booking anything themselves unless you want that |
| **Unused credit report** | "These students have large unused make-up balances" — so you can reach out proactively rather than being surprised later |
| **Digital intake forms** | Parents fill out enrollment/medical info digitally with a signature, instead of staff transcribing paper forms |
| **Automated waitlist alerts** | When a spot opens, staff see ranked matching candidates immediately instead of scanning manually |

**Anything missing from this list?** If there's something you've wanted for years that isn't here, that's probably the most valuable thing on this page.

| Part 4: Screenshots That Would Help |
| :---- |

*Round 2 (2026-09-10) returned eight screenshots: the report buttons, the absence lookup, the Regional Center payment spreadsheet, a student attendance layout, group classes on the Deck Manager schedule, a student account with its waitlist section, the waitlist report, and the fmSMS screen (which names the gateway: Twilio). They contain family names and contact details, so they live only in the gitignored original of the Round 2 document.*

If it's easy to grab these while you're working, they'd help a lot. No need to stage anything — normal working screens are ideal.

* The **Family tab** on a student record (we've only seen the Lessons tab)

* The **billing/payment entry screen** — where payments actually get recorded

* Any **reports** you run regularly (payments due, monthly summaries, etc.)

* The **waitlist screen** as you actually use it

* The **fmSMS bulk texting screen** — particularly the **Accounts** or **Gateways** tab, which tells us which texting service is connected

* **Anything you use for charter school or Regional Center billing** — even if it's a spreadsheet, a Word invoice template, or a folder of PDFs outside FileMaker entirely. Especially that, actually: if it lives outside the system, we have no visibility into it at all.

* Anything that's a daily annoyance — a screenshot of the thing you wish worked better

*Thanks — every answer here directly shapes what gets built. Nothing is too small or too obvious to mention.*