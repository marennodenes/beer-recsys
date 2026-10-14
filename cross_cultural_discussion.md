# Cross-cultural discussion

## How the project is cross-cultural

We train on users outside Norway and recommend beers to new Norwegian users. This is cross-country transfer, as
described in the course. We use two country signals:

- **User country:** from the user's profile location.
- **Beer country:** from the brewery's location.

## Limits of using country as culture

- Profile country is where the user lives, not their nationality or where they drank the beer.
- Beer country is where the beer was brewed, not the brand. Mikkeller (Danish) beers brewed at Lervig count as
  Norwegian.
- People in the same country do not all have the same taste.

## Why we did not use the World Values Survey

1. **One target country.** A country-level score is the same for every Norwegian test user, so it cannot change
   the ranking or be tested.
2. **Values are not taste.** It is not clear that values such as trust are linked to beer preference.

Instead, we test culture through beer country (H2) and data from similar countries (H3).

## What the results say

**H2: bonus for Norwegian beers.** The bonus makes BPR much better (NDCG +43 %). But this may be about what is
sold in Norway, not taste. Norwegian beers are 29 % of all hidden beers and 28 % of liked ones. Norwegians drink a
lot of Norwegian beer, but do not like it more.

**H3: Nordic data.** Nordic data beats the same amount of other data (NDCG +62 %). Part of this may not be taste:

- Nordic data contains more of the beers Norwegians rate: 87 % of hidden beers, against 74 % for E.
- Nordic users rate Norwegian beer three times as often (2.8 % against 0.9 % of ratings).
- D has fewer users with longer histories (about 400 ratings each) than E (about 43 each).

**In short:** country matters, but we cannot separate taste from availability.

## Business meaning

A beer app entering Norway can start without Norwegian data. A popular list from other countries is a strong
start. Data from nearby countries is worth more than the same amount from far away.

## Future work

- Test several target countries, so country-level features like WVS can be tested.
- Compare several source regions of the same size.
- Sample whole users for E, not single ratings.
