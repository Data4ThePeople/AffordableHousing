---
title: "Rentals Within Reach: Visualizing the Affordability of Rentals Where You Live"
subtitle: "A free map of every U.S. county shows how many rentals a household can afford at 30% of its income, and how that has changed since 2005."
slug: rentals-within-reach
date: 2026-10-08
section: Data 4 Thought, Visualization
hero: images/rentals-within-reach-hero-1680x1080.png
hero_alt: "Dark map of the United States with one bubble per county, sized by its number of rentals and colored by the share the median renter household can afford in 2020-2024. Most large bubbles, including Los Angeles, Phoenix, Houston, South Florida, Chicago and the Northeast, are dark red or red, meaning under 40% within reach. Smaller yellow and orange bubbles dot the Midwest. Text: Rentals Within Reach. In 1,960 of 3,141 counties the median renter household can afford fewer than half the rentals."
meta_title: "Rent Affordability by County: Free Map, 2005 to 2024"
description: "Free interactive map of every U.S. county: the share of rentals a household can afford at 30% of income, 2005-2009 to 2020-2024. Enter your own income."
keywords: rent affordability by county, how much rent can I afford by county, affordable rentals map, rent affordability map, median renter income by county, share of rentals I can afford, rental housing affordability data, rent vs income by county
schema_type: dataset
dataset_name: Share of rental units a household can afford at 30% of income, every U.S. county, 2005-2009 to 2020-2024
dataset_description: "For 3,141 U.S. counties and county equivalents on 2024 boundaries, in four American Community Survey 5-year periods that share no sample (2005-2009, 2010-2014, 2015-2019, 2020-2024): renter-occupied units paying cash rent by gross rent bucket, set against a monthly rent ceiling of 30% of household income, for the median renter household, the median and four percentiles of all households, or any income entered. Income can be counted before or after federal and state income tax and payroll tax."
temporal: 2005/2024
spatial: United States
measured: Share of rentals priced at or under the rent ceiling|percent; Renter-occupied units paying cash rent, by gross rent bucket|count; Median renter household income|U.S. dollars; Household income at the 20th, 40th, 50th, 60th and 80th percentiles|U.S. dollars; Monthly rent ceiling|U.S. dollars; Change in rentals and in rentals priced within reach, 2005-2009 to 2020-2024|count and percent
sources: https://www.census.gov/programs-surveys/acs|https://taxsim.nber.org/taxsim35/|https://www.ssa.gov/oact/cola/cbb.html|https://www.bls.gov/cpi/|https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
distribution: text/html|https://data4thepeople.github.io/AffordableHousing/;application/json|https://github.com/Data4ThePeople/AffordableHousing/tree/main/data/processed
measurement_technique: ACS table B25063 gross rent buckets per county; rent ceiling is the chosen share of income divided by 12; rentals at or under the ceiling counted with straight-line interpolation inside the bucket the ceiling falls in; incomes from ACS tables B25119, B19013, B19080, B19001 and B25118; after-tax income from NBER TAXSIM 35 and Social Security Administration payroll tax rates for one wage earner; counties with changed boundaries joined or rebuilt from towns so every period is on 2024 boundaries
credit: Data 4 The People, from the U.S. Census Bureau, the National Bureau of Economic Research, the Social Security Administration and the U.S. Bureau of Labor Statistics
license: https://www.data4thepeople.com/terms-of-use
app_url: https://data4thepeople.github.io/AffordableHousing/
app_name: "Rentals Within Reach: interactive map, 2005-2009 to 2020-2024"
app_category: EducationalApplication
app_description: Free interactive map of the share of rentals a household can afford at 30% of its income, in every U.S. county, across four periods from 2005-2009 to 2020-2024.
app_features: Every U.S. county, four periods from 2005-2009 to 2020-2024|Play through the periods|Median renter household, median of all households, or four income percentiles|Enter any income|Income before or after taxes, for three household types|Slider for the share of income spent on rent|Hover or tap any county for the math|Rentals by monthly rent for each county|Change in rentals and in rentals within reach|Search any county by name|Filter to one state|Leave out college counties|Rankings of fewest and most within reach
drop_cap: false
heading_spacer: 20px
caption_spacer: 20px
dividers: false
---

# Rentals Within Reach: Visualizing the Affordability of Rentals Where You Live

We’ve heard the story.

Renters are getting squeezed.

In fact, I was [interviewed about this](https://www.data4thepeople.com/p/renters-are-falling-behind) months ago, right after the ACS 5-year survey data dropped covering the 2020-2024 period. I did the math at the national level, and learned two things:

1. The median U.S. homeowner household’s income ($100,009) is nearly twice that of the median U.S. renter household ($52,966).
2. Over the prior five years, the median monthly rent increased by 33.1%, while the median housing costs for homeowners increased by 20.9%.

Based on these two findings, and a whole lot more, I titled the post “Squeezed on Both Ends.” Because that’s what renters were facing – higher shelter price inflation and much lower absolute income to cover higher costs.

## From national data to local data

But that was way back on February 19, 2026 – the days before we discovered how to leverage AI to assist with our data journalism process. And so, I was stuck analyzing national data, which as I have said over and again, no one person actually experiences.

We can analyze national data to understand America.

But we must move to analyzing local data to understand Americans.

I want to understand Americans, not America. And as we show you five days a week, we now have the tools to do this.

## Meet Rentals Within Reach

That said, please meet the newest member of our visualization team – D4TP’s Rentals Within Reach visualization. It starts by asking one question – if your family earned the median renter’s household income and wanted to pay no more than 30% of your after-tax income on rent (a stricter take on the usual 30% rule of thumb), how many units in your county could you afford? The map shows you this. And all the red? Those are the counties where fewer than 40% of the total rental units in your county were in your price range.

<iframe src="https://data4thepeople.github.io/AffordableHousing/?v=20261008a#embed=1" width="100%" height="780" loading="lazy" style="border:0" title="Rentals Within Reach: interactive map of rentals a household can afford, by county, 2005-2009 to 2020-2024"></iframe>

::: spacer 40px

The map uses the Census Bureau’s American Community Survey 5-year estimates of gross rent and household income for every U.S. county, in four periods from 2005-2009 to 2020-2024. Rentals Within Reach is free to use, with no signup.

## How to use it

That’s just the default view. But this visualization is loaded with different bells and whistles that can help you explore this topic and really get a sense for how difficult it is to find an affordable rental across America.

Feel free to head over to [GitHub](https://github.com/Data4ThePeople/AffordableHousing) for step-by-step written instructions on how to use this new visualization. You’ll find the detailed methodology there too. But to save words today, we’ve created a one-minute tutorial video. We strongly encourage you to watch this to get a feel for everything this viz can do.

<iframe src="https://www.youtube-nocookie.com/embed/zs0lN6o3SdE?rel=0" width="100%" height="440" loading="lazy" style="border:0" title="How to use Rentals Within Reach (57-second video)" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

::: spacer 40px

## A thought experiment: An entry-level teacher looking for a place to live

There are so many stories we want to tell from this visualization. And we will tell many of them over time. But for now, we will just present a single thought experiment. This one comes from the mind of Data 4 The People founding data architect, Amanda Sinton, who, before she became a data scientist, was an elementary school teacher.

You live in Arizona and just graduated with your bachelor’s degree in education and are ready to go teach at an elementary school in Phoenix. But you need a place to live, and one that ideally you can pay for on 30% of what is left of your $53,000 salary after taxes. Your friend tells you about this neat new free tool at Data 4 The People, so you head over to the site, choose Arizona from the dropdown, plug your salary in (note: we have no access to any user-entered data! It all lives in your browser), set “Taxed as” to single and study the data.

![Dark map of Arizona counties as bubbles sized by number of rentals and colored by the share a $53,000 income can afford in 2020-2024 at 30% of after-tax income. Maricopa County, outlined, is the largest bubble and is dark red, meaning under 30% within reach. Pima County is red. Smaller counties range from orange and yellow to light green.](images/01-arizona-map-53k.png)
*Arizona counties on a $53,000 income, 2020-2024, at 30% of after-tax income for a single person. Maricopa County is outlined.*

You find out that of the 583,955 rental units in Maricopa County, you can afford just 14% at 30% of your post-tax income.

![Bar chart of Maricopa County rentals by monthly gross rent, 2020-2024. A dashed line marks a $1,087 monthly ceiling. Only the short bars to the left of the line are green; the tallest bars, between about $1,250 and $2,500 a month, are gray and to the right of the line. 14% of 583,955 rentals fall under the ceiling.](images/02-maricopa-rents-by-price.png)
*Maricopa County rentals by monthly rent. The dashed line is the $1,087 a month this income supports.*

But it gets worse. You scroll down the right panel and learn that over the past 15 years the units that you could have afforded on this salary, adjusted for inflation, have declined 32%, despite overall units increasing by 39%! So, overall rental units are way up in your county…just not ones you can afford.

![Two columns for Maricopa County, 2005-2009 to 2020-2024. All rentals rose by 162,376, or 39%, from 421,579 to 583,955. Rentals priced within reach of a $53,000 income, held in 2024 dollars, fell by 39,384, or 32%, from 121,440 to 82,056.](images/03-maricopa-change-in-rentals.png)
*From 2005-2009 to 2020-2024, Maricopa County added 162,376 rentals. The number priced within reach of this income fell by 39,384.*

### The choices from here

And so what do you do? Do you decide to shell out 50% of your income for a fancy Phoenix rental? If so, now you can afford 57% of all units… but how is that going to set you up for the future?

![The same dark map of Arizona counties with the share of income for rent raised to 50%. Maricopa County's bubble changes from dark red to yellow, meaning between 50% and 65% of rentals are within reach, and most other Arizona counties turn light green or dark green.](images/04-arizona-map-53k-at-50-percent.png)
*The same income at 50% of after-tax pay. The ceiling rises to $1,811 a month.*

Or, you could look a few counties away in Santa Cruz County. You may make just $45,000 per year there (pre-tax), but rental units are far cheaper. At your desired 30% of post-tax income level, 61% of the units there are in reach.

![County panel for Santa Cruz County, Arizona, 2020-2024, on a $45,000 income: $7,701 in income and payroll taxes, $37,299 after taxes, a rent ceiling of $932 a month, and 61% of rentals priced within reach. A bar chart of rentals by monthly rent shows most bars to the left of the ceiling line.](images/05-santa-cruz-45k.png)
*Santa Cruz County, Arizona, on $45,000: a $932 monthly ceiling.*

## What this does not tell you

The teacher's search would be harder than the map suggests in some ways, and the tool leaves some things out.

- **It counts rentals people live in now, not vacancies.** The Census Bureau records what current tenants pay. A unit rented at a low price for many years counts the same as one on the market today. The share a new arrival can find is very likely lower than the share shown.
- **A unit priced within reach may not be open.** Many low-rent units are already rented, some of them by households that earn more.
- **Size is not counted.** A studio and a three-bedroom count the same.
- **Taxes are estimated.** After-tax income is figured for one wage earner with no other income, using federal and state income tax and payroll tax. Local income taxes are left out.
- **Small counties are less certain.** Santa Cruz County has 4,690 rentals. Maricopa County has 583,955. Figures for small counties rest on fewer survey responses.

The full list of limits, and the method, is on [GitHub](https://github.com/Data4ThePeople/AffordableHousing).

## Try it yourself

This is how we understand Americans. We create the story and the tool to simulate their lives, and then see how it plays out. Are we missing elements of the story? Of course we are. These tools are not perfect. The only way to get to perfect is to actually live that other person’s life. But we can at least gain an appreciation for what they must have to go through using the data.

So, take this tool for a spin and go learn about Americans who you have never met. We are going to come back to this tool many times in the coming months. We have identified several amazing stories, and will get to them all in due time. But we’d love to see what you find first. Let us know if you come across a good story that opens your eyes to someone else’s lived experience and we may just publish it (with credit to you of course!).
