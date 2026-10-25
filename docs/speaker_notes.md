# Speaker notes: Two sides of Bologna's Airbnb market

Total talk time is about **6 minutes 40 seconds**, including the live demo.

| Slide | Time | Running total |
|---|---|---|
| 1. Title and name | 20 s | 0:20 |
| 2. Dataset overview | 50 s | 1:10 |
| 3. Problem definition | 40 s | 1:50 |
| 4. EDA results (5 panels) | 2 min 30 s | 4:20 |
| 5. Dashboard demo | 1 min | 5:20 |
| 6. Final insights | 50 s | 6:10 |
| 7. Conclusion | 30 s | 6:40 |

Keys: **→** or **Space** = next, **←** = back, **F** = fullscreen. On slide 4, → steps through the 5 panels first.

**Before the talk (10 minutes early):**
- Open https://bologna-airbnb.streamlit.app so the app wakes up.
- Open the slides and press **F**.

---

## 1. Title and name (20 s)
> Hi, I'm Khalid Alotaibi. My project looks at Bologna's Airbnb market from two sides: the people who **host** and the people who **stay**. If you want to follow along, the two QR codes open the live dashboard and these slides.

## 2. Dataset overview (50 s)
> The data comes from Inside Airbnb. It's a snapshot of every Bologna listing on 19 September 2026: 5,094 rows and 19 columns.
> I picked it because it's recent, it's messy in a realistic way, and hosts and guests read it differently.
> The bars show the cleaning. I removed 2 duplicate listings, 518 listings with no price, and 44 prices above €1,000; the highest was €10,000. That leaves **4,530 listings**.

## 3. Problem definition (40 s)
> I asked two sets of questions. The **host** wants to know who controls the market, which price range gets the most demand, and where the competition is.
> The **guest** wants to know what a night costs, which areas are cheaper, and how much a private room saves.
> The data has no booking numbers, so I measure **demand with reviews in the last 12 months**.

## 4. EDA results (2 min 30 s, about 30 s per panel)
**Host types:**
> Only 48 professional hosts run 28% of all listings. They charge €31 more a night than single hosts, but single hosts get 35% more reviews.

**Demand:**
> The cheapest places are not the busiest. Mid-range listings, €100 to €199, get a median of 10 reviews a year. Budget listings get only 3.

**Prices:**
> A typical night costs €176. I use the median because a few very expensive listings pull the mean up to €206. A private room saves about €55 a night.

**Where to stay:**
> On the map, 69% of listings are in the two central areas. The centre costs €70 more than Savena.

**Correlations:**
> Price hardly predicts demand: the correlation is only -0.09. The 0.86 just shows that two review columns measure the same thing.

## 5. Dashboard demo (1 min, live in the app)
Click **Open the live demo**. If there's no internet, use the screenshots on this slide.

1. **Story:** "The 5 findings, one at a time." Click next once.
2. **Compare:** pick two neighbourhoods, for example Santo Stefano and Savena. "The trophy marks the better value."
3. **Explore:** click one listing. "You see its details and whether the price is fair."
4. **Predict:** change the room type. "A Random Forest estimates the price. It's off by about €73 on average, 17% better than just guessing the median."

Come back to the slides with **Alt+Tab**.

## 6. Final insights (50 s)
> **For hosts:** price in the mid-range. Porto - Saragozza pairs a high price with the most reviews. Personal hosting stands out, with 35% more reviews.
> **For guests:** a private room saves €55, staying outside the centre saves €70, and check the minimum stay, because 329 listings only take stays of 30 nights or more.

## 7. Conclusion (30 s)
> Bologna's market rewards the middle. Clean first, use the median for skewed prices, and always compare a model with a baseline.
> The limits: one snapshot, listed prices rather than paid ones, and reviews only approximate demand. Next, I'd compare seasons and add the detailed listing data.
> Thank you. Any questions?
