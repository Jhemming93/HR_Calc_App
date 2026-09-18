# Highrise Gold Lab

A small, independent calculator for estimating Highrise item flips, grab expected value, and outright shop purchases. Open `index.html` directly in a browser or publish this repository using GitHub Pages. No build step or external dependencies.

## GitHub Pages

Go to **Settings → Pages → Build and deployment**. Choose **Deploy from a branch**, then select **main** and **/(root)** and save. GitHub will show the live URL on that page after the deployment finishes.

## Using it

- **Flip an item:** enter your purchase price, a realistic sale price, selling method, and desired profit. Marketplace and direct trade fees are editable.
- **Grab odds:** enter the price of one spin and every possible outcome with its probability and likely Marketplace resale price. Odds must sum to 100%. Unsellable outcomes should have a resale price of 0g.
- **Shop purchase:** compare the outright purchase price with an expected future player resale price; confirm tradeability and any trade lock in the game.

The app does not fetch live Highrise item prices. The default 30% Marketplace seller fee and 10% direct-trade buyer fee are based on [Highrise's trading guide](https://highrise.game/blog/how-to-trade-items-safely-on-the-highrise-marketplace); verify in-game rates before making a decision. Direct trades involving Gold Bars can have additional conversion costs. This project is not affiliated with Highrise.
