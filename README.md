# EzOptions-Schwab: Real-Time Options Analytics & Trading Dashboard

A professional-grade options trading dashboard that integrates with the Schwab API to deliver comprehensive real-time options flow analysis, Greek exposures, and market microstructure insights for active traders and market makers.

<div align="center">
  <a href="https://github.com/EazyDuz1t/EzOptions-Schwab">
    <img src="https://img.shields.io/github/stars/EazyDuz1t/EzOptions-Schwab" alt="GitHub Repo stars"/>
  </a>
</div>

---

## 🎯 What is EzOptions-Schwab?

EzOptions-Schwab is a Python-based web application that transforms complex options market data into actionable trading intelligence. By calculating and visualizing Greek exposures across the entire options chain, this tool helps traders understand:

- **Where market makers are positioned** and how they'll hedge their books
- **Key support and resistance levels** created by options positioning
- **Real-time shifts in market sentiment** through options flow
- **Dealer gamma exposure** that drives market volatility and price action
- **Volume-weighted positioning** showing where the most trading activity occurs

This is not just another options chain viewer—it's a sophisticated analytical platform that reveals the hidden forces driving market movement through options dealer hedging.

---

## 🚀 Core Capabilities

### 📊 Real-Time Market Data
- **Live Schwab API Integration** - Stream real-time options chain data directly from Schwab
- **Auto-Refreshing Price Updates** - Continuous 1-second interval updates during market hours
- **Multi-Ticker Support** - Analyze SPY, SPX, individual equities, and aggregate market indices
- **Intraday Price Charts** - Heikin-Ashi and traditional candlestick charts with volume
- **Historical Data Persistence** - SQLite database stores 5-minute interval snapshots

### 📈 Advanced Greek Exposure Analytics

#### **Gamma Exposure (GEX)**
The most critical metric for understanding market maker hedging flows:
- **Positive GEX** → Market makers sell into rallies, buy dips (stabilizing)
- **Negative GEX** → Market makers buy rallies, sell dips (amplifying moves)
- **Strike-Level GEX** → Identify key support/resistance from dealer hedging
- **Absolute GEX Overlay** → Visualize total gamma "walls" regardless of direction

*Trading Use Case:* Large positive GEX at a strike acts as a magnet—price tends to gravitate toward max gamma. Negative GEX environments create explosive volatility.

#### **Delta Exposure (DEX)**
Track the directional bias of options positioning:
- **Net Delta Exposure** → Shows cumulative directional exposure by strike
- **Dealer Positioning** → Understand if dealers are long or short delta
- **Flow Directionality** → Identify whether call buying or put buying dominates

*Trading Use Case:* Heavy call DEX suggests bullish positioning; heavy put DEX indicates hedging or bearish sentiment. Watch for DEX shifts that precede trend changes.

#### **Vanna Exposure (VEX)**
Cross-Greek sensitivity between volatility and spot price:
- **Vanna Shows Volatility-Price Relationship** → How delta changes with IV shifts
- **Volatility Skew Impact** → Understand how IV changes affect dealer hedging
- **Correlation Trading** → Identify when vol and spot will move together

*Trading Use Case:* Positive vanna means dealers buy the underlying when IV rises, creating positive feedback loops. Critical during volatility spikes.

#### **Advanced Third-Order Greeks**
For sophisticated traders who need deeper insights:

- **Charm (Delta Decay)** - How delta changes with time, revealing theta-related hedging flows
- **Speed (Gamma of Gamma)** - Rate of change of gamma, predicting acceleration in dealer hedging
- **Vomma (Vega of Vega)** - Convexity of volatility exposure, critical for vol-of-vol trading
- **Color (Gamma Decay)** - Time decay of gamma, shows when GEX effects will weaken

*Trading Use Case:* These higher-order Greeks help predict how dealer hedging pressure will evolve as time passes and market conditions change.

### 🕒 Historical Bubble Level Tracking
Unique feature that captures intraday exposure evolution:
- **5-Minute Interval Snapshots** - Store GEX, DEX, VEX at each strike throughout the session
- **Time-Series Bubble Charts** - Visualize how exposure has shifted during the day
- **Strike Migration Tracking** - See how max gamma levels move with price
- **Market Hours Only** - 9:30 AM - 4:00 PM ET data collection

*Trading Use Case:* Identify when large positions are established or unwound. Track how gamma walls build up or dissolve as expiration approaches.

### 📍 Volume-Weighted Centroid Analysis
Discover where the real money is flowing:
- **Call Centroid** - Volume-weighted average strike of all call activity
- **Put Centroid** - Volume-weighted average strike of all put activity
- **Intraday Tracking** - See how centroids shift throughout the trading day
- **Sentiment Indicator** - Compare centroids to spot price for positioning bias

*Trading Use Case:* If the call centroid is rising while price is flat, smart money is positioning for upside. Centroids reveal where large players are concentrating their bets.

### 🎯 Market Aggregation Modes
Combine multiple tickers for broad market analysis:

**MARKET Mode** - Aggregates SPX + SPY with intelligent normalization:
- Combines two most liquid index products
- Per-Greek normalization ensures proportional weighting
- Notional exposure conversion for apples-to-apples comparison

**MARKET2 Mode** - SPY-only analysis for cleaner single-instrument view

*Trading Use Case:* Institutional flow is split across SPX and SPY. Aggregation mode shows the true institutional positioning across both vehicles.

---

## 🎨 Interactive Visualization Features

### Dynamic Strike Range Filtering
- **Adjustable Range**: 1% to 20% around current price
- **Smart Strike Rounding**: Automatically groups by natural strike intervals ($1, $5, $10)
- **Real-Time Recalculation**: Instantly update charts as price moves

### Multi-Chart Dashboard
- **Price Chart**: Candlesticks with volume, overlaid with gamma levels
- **Exposure Charts**: Side-by-side or stacked comparison of GEX/DEX/VEX
- **Horizontal Mode**: Display strikes vertically for better readability
- **Full Chain Table**: Sortable options chain with all Greeks and pricing

### Customizable Color Schemes
Three intensity modes for optimal visualization:
- **Solid** - Uniform color for clean presentation
- **Linear Intensity** - Proportional opacity based on exposure magnitude
- **Ranked Intensity** - Exponential scaling that highlights only the largest exposures

### Exposure Calculation Options
- **Open Interest Weighting (Default)** - Shows dealer positioning from existing contracts
- **Volume Weighting** - Reveals today's flow and recent activity
- **Delta-Adjusted** - Scales exposures by moneyness for ITM/OTM comparison
- **Notional vs. Share Basis** - Toggle between dollar exposure and share exposure

---

## 💼 Trading Use Cases

### 1. **Identifying Support & Resistance Levels**
**How:** Look for strikes with the highest positive GEX
**Why:** Market makers will hedge against gamma at these strikes, creating price stability
**Example:** If SPY has massive GEX at 580 strike, price will likely consolidate around 580 as dealers hedge

### 2. **Predicting Volatility Expansion**
**How:** Monitor for negative net gamma environments
**Why:** Negative gamma forces dealers to chase price, amplifying moves
**Example:** After a large put buying surge creates negative GEX, expect larger-than-normal price swings

### 3. **Spotting Smart Money Flow**
**How:** Watch the volume-weighted centroids shift
**Why:** Centroids reveal where sophisticated players are positioning
**Example:** Call centroid rising from 580 to 590 while SPY trades 575 suggests institutions expect upside

### 4. **Timing Options Trades**
**How:** Use charm and color to see when gamma will decay
**Why:** Gamma walls weaken as expiration approaches, changing support/resistance
**Example:** High charm at Wednesday close means Thursday's gamma profile will look very different

### 5. **Understanding Volatility Surface Dynamics**
**How:** Monitor vanna exposure during IV regime changes
**Why:** Vanna creates feedback loops between volatility and price
**Example:** Positive vanna means rising IV forces dealers to buy, creating upside momentum

### 6. **Analyzing Multi-Leg Strategy Exposure**
**How:** Use delta-adjusted views to see net directional risk
**Why:** Understand true market exposure after accounting for ITM probability
**Example:** A large OTM call position looks smaller after delta adjustment, revealing true risk

### 7. **Pre-FOMC / Event Positioning**
**How:** Check historical bubble levels before major announcements
**Why:** See how positioning evolved leading up to the event
**Example:** Gamma walls building ahead of Fed decision show where dealers are most exposed

---

## 💰 How to Use This Tool for Profitable Trading

This section provides actionable trading strategies and workflows to translate gamma exposure analysis into profitable trading decisions.

---

### 🎯 The Core Trading Framework

#### Understanding Dealer Positioning

Market makers (dealers) are the counterparty to most retail and institutional options trades. They operate with a key objective: **remain delta-neutral while profiting from theta decay and bid-ask spread.**

**Critical Concept:** Dealers dynamically hedge their books by buying/selling the underlying asset. This hedging activity creates predictable price behavior that you can exploit.

---

### 📋 Daily Trading Workflow

#### **Pre-Market Routine (8:00 AM - 9:30 AM ET)**

**1. Load Your Watchlist Tickers**
- Start with SPY or SPX for overall market gamma profile
- Add any individual stocks you're actively trading
- Use MARKET mode to see combined institutional positioning

**2. Analyze Net Gamma Exposure**
```
Positive Net GEX = Dealers SHORT gamma → They sell rallies, buy dips → RANGE-BOUND DAY
Negative Net GEX = Dealers LONG gamma → They buy rallies, sell dips → TRENDING DAY
```

**Action:**
- **Positive GEX:** Plan for range-bound strategies (iron condors, strangles, butterflies)
- **Negative GEX:** Prepare for directional plays (long calls/puts, vertical spreads)

**3. Identify Key Strike Levels**
- Note the strike with **maximum positive GEX** → Strong support/resistance
- Note strikes with **high absolute GEX** → Price magnets
- Mark strikes with **negative GEX** → Potential breakout zones

**4. Check Volume Centroids**
- If call centroid > current price: Bullish positioning
- If put centroid < current price: Bearish/hedging activity
- Watch for shifts in centroid position as market opens

---

#### **Market Open - First Hour (9:30 AM - 10:30 AM ET)**

**5. Enable Real-Time Streaming**
- Click "Start Streaming" for 1-second updates
- Watch how GEX levels change with early volume
- Monitor centroid shifts as institutional flow enters

**6. Observe Price Behavior at Key Strikes**

**Scenario A: Price Approaching Max GEX Strike**
- **Setup:** SPY at 578, max GEX at 580
- **Behavior:** Price will likely struggle to break through 580
- **Trade:** Sell 580 calls, or buy iron condor with 580 as center
- **Risk:** If volume surge breaks through GEX wall, momentum accelerates

**Scenario B: Price Between Two GEX Walls**
- **Setup:** Strong GEX at 575 and 585, SPY trading at 580
- **Behavior:** Price oscillates in range
- **Trade:** Sell strangle (575P/585C), buy butterflies centered at 580
- **Risk Management:** Exit if GEX profile changes (walls dissolve)

**Scenario C: Price in Negative GEX Zone**
- **Setup:** Net GEX negative, no major walls nearby
- **Behavior:** Explosive moves, dealer hedging amplifies momentum
- **Trade:** Buy ATM straddles/strangles, or directional options
- **Stop Loss:** Exit if move stalls and GEX turns positive

---

#### **Mid-Day Monitoring (10:30 AM - 2:00 PM ET)**

**7. Track Historical Bubble Levels**
- Enable "Show Historical Bubbles" for GEX chart
- Look for gamma accumulation or dissolution at key strikes
- Identify if new walls are being built (new positioning)

**8. Use Delta Exposure for Directional Bias**
```
Heavy Call DEX = Market is net long calls = Bullish skew
Heavy Put DEX = Market is net long puts = Defensive positioning
```

**Trading Signal:**
- **Rising Call DEX + Price stable:** Institutions loading calls → Prepare for rally
- **Rising Put DEX + Price stable:** Smart money hedging → Potential pullback

**9. Monitor Vanna Exposure During Vol Changes**

**Vanna Trading Strategy:**
- **High Positive Vanna + VIX Spike:** Dealers forced to buy → Amplifies upward moves
- **High Negative Vanna + VIX Spike:** Dealers forced to sell → Amplifies downward moves

**Action:**
- If VIX is rising and vanna is positive at current strike → Buy calls
- If VIX is rising and vanna is negative → Buy puts
- Trade expires when volatility normalizes

---

#### **Power Hour (3:00 PM - 4:00 PM ET)**

**10. Check for Pin Risk**
- Look at 0DTE (same-day expiration) GEX if available
- Price often "pins" to max GEX strike into close on expiration Friday
- **Trade:** If price is near max GEX strike, sell options (high theta, low movement expected)

**11. Assess Tomorrow's Gamma Profile**
- Use **Charm** exposure to predict how today's GEX will decay overnight
- High charm = significant gamma decay → Support/resistance levels will weaken
- Plan next day's trades based on evolving gamma landscape

---

### 🎓 Advanced Trading Strategies

#### **Strategy 1: Gamma Scalping**

**Objective:** Profit from dealer hedging by trading with their flow

**Setup:**
1. Identify strike with massive positive GEX (e.g., SPY 580 with $2B GEX)
2. Price approaches from below (e.g., SPY at 578)
3. Enable streaming to watch real-time

**Execution:**
- **As price rises toward 580:** Dealers sell underlying to maintain neutrality
- **Trade:** Short stock/ETF or buy puts as price reaches 579.50-579.80
- **Target:** Price reversal back to 578-579
- **Stop Loss:** 580.50 (GEX wall breached)

**Why It Works:** Dealers' selling pressure creates resistance, causing mean reversion.

---

#### **Strategy 2: Breakout Trading in Negative Gamma**

**Objective:** Catch explosive moves when dealers amplify momentum

**Setup:**
1. Identify negative net GEX environment (dealers long gamma)
2. Price consolidating near a strike with minimal GEX (no wall)
3. Wait for catalyst (news, economic data, etc.)

**Execution:**
- **Buy ATM straddle/strangle** before catalyst
- **Or:** Buy directional option (call/put) based on expected news direction
- Dealers will chase the initial move, creating momentum
- **Exit:** When price reaches next major GEX wall or volatility collapses

**Example:**
- Net GEX = -$500M (negative)
- SPY at 580, no GEX walls until 575 and 585
- FOMC announcement at 2:00 PM
- **Trade:** Buy 580 straddle at 1:55 PM, sell when SPY hits 575 or 585

---

#### **Strategy 3: Volatility Mean Reversion with Vanna**

**Objective:** Trade the vol-spot correlation created by vanna exposure

**Setup:**
1. High positive vanna exposure at current strike
2. VIX spikes (e.g., VIX jumps from 15 to 20)
3. Underlying price hasn't moved yet (lag)

**Execution:**
- **Vanna forces dealers to buy underlying as IV rises**
- **Trade:** Buy calls immediately after VIX spike
- Price will follow volatility higher due to vanna feedback loop
- **Exit:** When VIX normalizes or vanna exposure decreases

**Risk Management:** Use tight stops; if price doesn't respond in 1-2 hours, exit.

---

#### **Strategy 4: Event Trading with Historical Bubbles**

**Objective:** Understand how positioning builds before major events

**Setup:**
1. Major event scheduled (FOMC, CPI, earnings)
2. Review historical bubbles 1-2 days before event
3. Track where gamma is accumulating

**Analysis:**
- **Gamma building at higher strikes:** Market expects upside
- **Gamma building at lower strikes:** Market expects downside
- **Gamma building at current strike:** Market expects no move (sell premium)

**Execution:**
- **If bullish gamma:** Buy call spreads targeting those strikes
- **If bearish gamma:** Buy put spreads targeting those strikes
- **If flat gamma:** Sell straddles/strangles at current price

---

#### **Strategy 5: Centroid Divergence Trading**

**Objective:** Follow smart money by tracking volume-weighted positioning

**Setup:**
1. Monitor call and put centroids throughout the day
2. Look for divergence between centroid and spot price

**Bullish Signal:**
```
Call Centroid: Rising (e.g., 580 → 585 → 590)
Spot Price: Flat or slightly higher (e.g., 578 → 579)
Interpretation: Institutions loading OTM calls, expecting rally
```

**Trade:** Buy calls at current price or slightly OTM

**Bearish Signal:**
```
Put Centroid: Falling (e.g., 575 → 570 → 565)
Spot Price: Flat or slightly lower (e.g., 578 → 577)
Interpretation: Institutions loading OTM puts, expecting selloff
```

**Trade:** Buy puts at current price or slightly OTM

**Timing:** Centroids are early indicators; price often follows within 1-3 hours

---

### 🛡️ Risk Management Rules

#### **Position Sizing**
- **Never risk more than 2-5% of account on single trade**
- Gamma-based trades are directional; losses can be swift
- Use defined-risk strategies (spreads) when learning

#### **Stop Losses**
- **GEX wall breach:** Exit immediately if price closes above/below key gamma level
- **Time-based stops:** If trade thesis doesn't play out in 1-2 hours, exit
- **Volatility stops:** If VIX spikes/collapses unexpectedly, reassess

#### **Profit Taking**
- **Take 50% off at 1R (1x your risk):** Lock in profits early
- **Trail stops on remainder:** Let winners run with protection
- **Exit at target GEX strikes:** Take profits when price reaches predicted level

#### **Avoid These Mistakes**
1. **Ignoring changing gamma profiles:** Update analysis every 15-30 minutes
2. **Trading against major GEX walls:** Requires massive volume to break
3. **Overleveraging in negative GEX:** Moves can be explosive and unpredictable
4. **Forgetting about time decay:** Charm erodes gamma overnight
5. **Trading without stops:** Always define your max loss

---

### 📊 Real-World Example: Full Trade Walkthrough

#### **Date:** Hypothetical Friday, 0DTE Options Expiring

**Pre-Market Analysis (9:00 AM):**
```
Ticker: SPY
Price: $578.50
Net GEX: +$1.2B (positive - range-bound expected)
Max GEX Strike: $580 with $800M
Second GEX Strike: $575 with $400M
Call Centroid: $583 (bullish positioning)
Put Centroid: $574 (moderate hedging)
VIX: 14.5 (low vol environment)
```

**Trade Thesis:**
- Strong GEX wall at 580 will act as resistance
- 575-580 range is likely for the day
- Call centroid suggests institutions expect eventual break higher
- Plan: Sell premium in range, be ready to flip bullish if 580 breaks

**Trade 1 (9:35 AM): Sell 580/582 Call Spread**
- SPY opens at 578.80, rallies toward 579.50
- Sell 580C, buy 582C for $0.60 credit
- Max profit: $60/contract if SPY closes below 580
- Max loss: $140/contract if SPY closes above 582

**10:30 AM Update:**
- SPY hits 579.90, bounces off 580 (GEX wall working)
- Historical bubbles show gamma accumulating at 580 (wall strengthening)
- **Action:** Hold trade, wall is intact

**12:00 PM Update:**
- SPY at 579.20, volume surges, call centroid shifts to $585
- Unusual call buying detected via volume spikes
- **Action:** Close 580/582 spread for $0.40 profit (67% gain in 2.5 hours)

**Trade 2 (12:15 PM): Buy 581 Calls**
- Centroid shift + volume suggests breakout imminent
- Buy 581C for $1.20 (ATM strike above GEX wall)
- Stop loss: $0.60 if SPY drops below 578
- Target: 585 (next resistance, 50% risk)

**2:00 PM Update:**
- SPY breaks 580 on heavy volume, GEX wall collapses
- Price accelerates to 582.50 (dealers forced to chase)
- 581C now worth $2.80

**Action:** Sell 50% at $2.80 (133% gain), trail stop on rest

**3:30 PM Close:**
- SPY reaches 584, 581C worth $3.50
- Sell remaining at $3.40 (stop triggered on pullback)
- Final P&L: Trade 1 = $40/contract, Trade 2 = $180/contract average

**Lessons:**
- Respected GEX wall initially (sell premium strategy)
- Recognized regime change when wall broke (flipped bullish)
- Used centroid shift as early signal
- Took profits in stages (risk management)

---

### 🧠 Mental Models for Success

#### **Think Like a Market Maker**
- Ask: "If I were short these options, how would I hedge?"
- Dealers are predictable; they must hedge mechanically
- Your edge is knowing *when* and *how* they'll hedge

#### **Gamma Profile = Road Map**
- High GEX strikes are speed bumps (slows price down)
- Negative GEX zones are highways (price accelerates)
- Centroids show where the traffic is headed

#### **Volatility and Gamma Are Linked**
- High vol → Wider gamma → Stronger support/resistance
- Low vol → Concentrated gamma → Tighter ranges
- Vanna connects vol changes to directional pressure

#### **Time Erodes Everything**
- Today's gamma wall is tomorrow's minor bump (charm)
- Expiration day amplifies gamma effects (0DTE = maximum impact)
- Weekend theta decay weakens Friday's levels for Monday

---

### ⚡ Quick Reference: Gamma Signals

| Signal | Interpretation | Action |
|--------|---------------|--------|
| **Net GEX > $1B** | Strong support/resistance | Sell premium, range trades |
| **Net GEX < -$500M** | Volatility expansion likely | Buy options, expect big moves |
| **Price at Max GEX** | Strong pin risk | Sell straddles/strangles |
| **Price between GEX walls** | Oscillation expected | Iron condors, butterflies |
| **GEX wall breaks on volume** | Regime change | Flip direction immediately |
| **Call centroid rising** | Bullish positioning | Buy calls, target centroid |
| **Put centroid falling** | Bearish positioning | Buy puts, target centroid |
| **High vanna + VIX spike** | Vol-spot feedback loop | Trade direction of vanna sign |
| **High charm at close** | Tomorrow's gamma weak | Don't rely on same levels next day |
| **Bubbles accumulating** | Large position building | Watch for breakout/breakdown |

---

### 📈 Performance Tracking

**Keep a Trading Journal with These Metrics:**
1. **GEX profile at entry** (positive/negative, key strikes)
2. **Entry price vs. nearest GEX wall** (distance matters)
3. **Centroid position** (above/below price)
4. **VIX level** (volatility regime)
5. **Outcome** (did price respect GEX levels?)

**Analyze Monthly:**
- Win rate when trading with GEX walls vs. against them
- Profitability in positive vs. negative GEX environments
- Accuracy of centroid signals
- Best time of day for your strategies

---

### 🎯 Final Pro Tips

1. **Combine Multiple Signals:** GEX + Centroid + Vanna = highest probability setups
2. **Respect the Trend:** Gamma can slow trends but rarely reverses them permanently
3. **Watch for Volume:** GEX walls break on heavy volume; light volume = wall holds
4. **Trade Liquid Tickers:** SPY, QQQ, AAPL have most reliable gamma effects
5. **Expiration Matters:** Gamma effects strongest on Friday (weekly expiration)
6. **Backtest Your Ideas:** Use historical bubbles to validate your theories
7. **Stay Flexible:** Gamma profiles change; update analysis frequently
8. **Start Small:** Master 1-2 strategies before adding complexity
9. **Focus on Process:** Profits follow when you execute your plan consistently
10. **Never Stop Learning:** Review every trade, successful or not

---

**Remember:** This tool provides the map, but you must navigate. Combine gamma analysis with technical analysis, fundamentals, and market context for best results.

---

## ⚙️ Technical Architecture

### Backend Stack
- **Flask** - Lightweight Python web framework for API and HTML rendering
- **Schwabdev** - Python SDK for Schwab API integration
- **Pandas & NumPy** - Data manipulation and numerical calculations
- **SciPy** - Statistical functions for Black-Scholes Greek calculations
- **SQLite** - Local database for historical interval and centroid data

### Frontend Stack
- **Plotly.js** - Interactive charting library with D3.js under the hood
- **Vanilla JavaScript** - Client-side UI logic and real-time updates
- **Responsive HTML/CSS** - Single-page application with dynamic updates

### Options Mathematics
All Greeks calculated using **Black-Scholes-Merton model** with:
- **Eastern Time zone awareness** for accurate time-to-expiration
- **Continuous dividends** (q parameter) where applicable
- **Risk-free rate** of 2% (configurable)
- **Per-contract notional conversion** (100 shares per contract)

### Data Flow
1. **API Polling** - Fetch options chain from Schwab API
2. **Greek Calculation** - Compute all first, second, and third-order Greeks
3. **Exposure Aggregation** - Sum weighted exposures by strike
4. **Database Storage** - Persist 5-minute snapshots for historical analysis
5. **Chart Rendering** - Generate Plotly JSON for interactive visualization
6. **Client Update** - Push data to browser via AJAX polling

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/EazyDuz1t/EzOptions-Schwab
   cd ezoptions-schwab
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SCHWAB_APP_KEY=your_app_key_here
   SCHWAB_APP_SECRET=your_app_secret_here
   SCHWAB_CALLBACK_URL=your_callback_url_here
   ```

## Schwab API Setup

1. **Create a Schwab Developer Account**
   - Visit [Schwab Developer Portal](https://developer.schwab.com/)
   - Register for a developer account
   - Create a new application

2. **Get API Credentials**
   - App Key (Consumer Key)
   - App Secret (Consumer Secret)
   - Callback URL (for OAuth)

3. **Configure OAuth**
   - Set up the callback URL in your Schwab app settings
   - Ensure your callback URL matches the one in your `.env` file

## Usage

1. **Start the application**
   ```bash
   python ezoptionsschwab.py
   ```

2. **Access the dashboard**
   - Open your browser to `http://localhost:5001`
   - The application will start on port 5001 by default

3. **Using the Dashboard**
   - Enter a ticker symbol (e.g., SPY, SPX, AAPL)
   - Select expiration dates from the dropdown
   - Adjust strike range using the slider
   - Toggle different chart types and options
   - Enable/disable auto-update streaming

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Schwab Developer Account with API credentials
- Active brokerage account (for OAuth authentication)

### Step 1: Install Dependencies

```bash
# Clone the repository
git clone https://github.com/EazyDuz1t/EzOptions-Schwab
cd EzOptions-Schwab

# Install required packages
pip install -r requirements.txt
```

**Dependencies:**
- `flask` - Web framework
- `pandas` - Data manipulation
- `plotly` - Interactive charts
- `scipy` - Statistical calculations
- `schwabdev` - Schwab API client
- `python-dotenv` - Environment variable management
- `pytz` - Timezone handling
- `kaleido` - Static image export (optional)

### Step 2: Obtain Schwab API Credentials

1. Visit [Schwab Developer Portal](https://developer.schwab.com/)
2. Register for a developer account
3. Create a new application
4. Note your credentials:
   - **App Key** (Consumer Key)
   - **App Secret** (Consumer Secret)
   - **Callback URL** (for OAuth redirect)

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```env
SCHWAB_APP_KEY=your_app_key_here
SCHWAB_APP_SECRET=your_app_secret_here
SCHWAB_CALLBACK_URL=https://127.0.0.1:5001/callback
```

**Important:** The callback URL must match exactly what you configured in the Schwab Developer Portal.

### Step 4: Run the Application

```bash
python ezoptionsschwab.py
```

The application will:
1. Initialize the SQLite database (`options_data.db`)
2. Start the Flask web server on port 5001
3. Open OAuth flow for first-time authentication (if needed)
4. Launch the dashboard at `http://localhost:5001`

### First-Time OAuth Setup

On first run, the Schwab API will require OAuth authentication:
1. A browser window will open to Schwab's login page
2. Log in with your brokerage credentials
3. Authorize the application
4. You'll be redirected back to the application
5. Tokens are stored locally for future use

---

## 📖 Usage Guide

### Basic Workflow

1. **Access the Dashboard**
   - Navigate to `http://localhost:5001` in your browser
   - The interface loads with default settings (SPY ticker)

2. **Select a Ticker**
   - Enter any valid ticker symbol (SPY, SPX, AAPL, etc.)
   - Special tickers:
     - `MARKET` - Aggregates SPX + SPY
     - `MARKET2` - SPY only
   - Click "Update" or press Enter

3. **Choose Expiration Dates**
   - Dropdown populates with available expiration dates
   - Select one or multiple expirations
   - Charts update to show combined exposure across selected dates

4. **Adjust Strike Range**
   - Use slider to set percentage range around current price
   - Range: 1% to 20%
   - Narrower ranges provide more detail; wider ranges show full picture

5. **Customize Visualization**
   - **Show/Hide**: Toggle calls, puts, or net exposure
   - **Coloring Mode**: Choose Solid, Linear Intensity, or Ranked Intensity
   - **Chart Orientation**: Switch between vertical and horizontal layouts
   - **Exposure Metric**: Toggle between Open Interest and Volume weighting

6. **Enable Auto-Update**
   - Click "Start Streaming" for real-time 1-second updates
   - Charts refresh automatically with latest market data
   - Useful during active trading hours

### Advanced Features

#### Historical Bubble Levels
- View intraday evolution of exposure by strike
- Bubble size represents exposure magnitude
- Color represents call vs. put exposure
- Time axis shows market hours (9:30 AM - 4:00 PM ET)
- Click "Show Historical Bubbles" to enable

#### Volume Centroid Tracking
- Displays volume-weighted average strike for calls and puts
- Updates every 5 minutes during market hours
- Compare centroids to spot price for sentiment gauge
- Rising call centroid = bullish positioning

#### Absolute GEX Area Chart
- Overlay showing total gamma regardless of direction
- Gray shaded area behind bar charts
- Helps identify "gamma walls" where dealers are maximally exposed
- Toggle "Show Abs GEX Area" to enable

#### Max Level Highlighting
- Automatically highlights the strike with maximum exposure
- Choose between Absolute mode (largest magnitude) or Net mode
- Customizable highlight color (default: purple)
- Useful for identifying key support/resistance

#### Delta-Adjusted Exposures
- Scales all Greeks by their delta (ITM probability)
- Shows "effective" exposure accounting for moneyness
- Useful for comparing near-the-money vs. far-OTM strikes
- Toggle "Delta Adjusted" checkbox

#### Fullscreen & Popout Windows
- Click fullscreen icon on any chart to maximize
- Open charts in separate windows for multi-monitor setups
- Popout windows maintain real-time updates
- Useful for watching multiple exposures simultaneously

### Chart Types Explained

#### **Price Chart**
- Real-time candlestick or Heikin-Ashi price action
- Volume bars overlaid below price
- Gamma levels plotted as horizontal lines
- Spot price indicated with dashed line

#### **Gamma Exposure (GEX) Chart**
- Green bars = Call gamma (dealers short gamma)
- Red bars = Put gamma (dealers long gamma)
- Net bars = Call gamma minus Put gamma
- Positive net = Stabilizing; Negative net = Destabilizing

#### **Delta Exposure (DEX) Chart**
- Shows directional exposure by strike
- Net delta reveals dealer positioning (long vs. short)
- Large positive DEX = Bullish skew; Large negative DEX = Bearish skew

#### **Vanna Exposure (VEX) Chart**
- Cross-Greek showing vol-spot correlation
- Positive vanna = Dealers buy when IV rises
- Critical during volatility events and skew shifts

#### **Charm / Speed / Vomma / Color Charts**
- Third-order Greeks for advanced analysis
- Charm = Delta decay; Speed = Gamma acceleration
- Vomma = Vol convexity; Color = Gamma decay
- Use these to predict how today's exposures will change tomorrow

#### **Options Chain Table**
- Full list of all options contracts
- Sortable by strike, volume, OI, Greeks, price
- Real-time bid/ask/last prices
- Implied volatility for each contract

---

## ⚙️ Configuration Options Reference

### Dashboard Settings (Top Panel)

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Ticker** | Any valid symbol | SPY | Asset to analyze |
| **Expiration** | Available dates | Nearest | Options expiration date(s) |
| **Strike Range** | 1% - 20% | 5% | Percentage around spot price |
| **Exposure Metric** | Open Interest / Volume | Open Interest | Weighting for Greek calculations |
| **Delta Adjusted** | On / Off | Off | Scale Greeks by delta |
| **Notional** | On / Off | On | Calculate in dollars vs. shares |
| **Coloring Mode** | Solid / Linear / Ranked | Solid | Opacity/intensity style |
| **Call Color** | Hex color | #00FF00 | Color for call exposures |
| **Put Color** | Hex color | #FF0000 | Color for put exposures |

### Chart-Specific Toggles

| Toggle | Default | Effect |
|--------|---------|--------|
| **Show Calls** | On | Display call exposures |
| **Show Puts** | On | Display put exposures |
| **Show Net** | On | Display net (calls - puts for GEX) |
| **Horizontal Mode** | Off | Rotate chart 90° (strikes on Y-axis) |
| **Show Abs GEX Area** | Off | Overlay total gamma area chart |
| **Highlight Max Level** | Off | Mark strike with max exposure |
| **Show Bubbles** | Off | Display historical intraday data |

### Auto-Update Controls

- **Streaming Enabled**: Updates every 1 second during market hours
- **Manual Update**: Click "Update" button to refresh once
- **Pause/Resume**: Toggle streaming on/off without losing settings

### Persistent Settings

The application automatically saves your preferences:
- Ticker selection
- Strike range
- Color scheme
- Chart toggles
- Exposure metric choice

Settings persist across browser sessions and are loaded on startup.

---

## 📊 Database Schema

The application uses SQLite with two main tables:

### `interval_data` Table
Stores 5-minute snapshots of exposure by strike:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `ticker` | TEXT | Ticker symbol |
| `timestamp` | INTEGER | Unix timestamp (rounded to 5-min intervals) |
| `price` | REAL | Spot price at time of snapshot |
| `strike` | REAL | Option strike price |
| `net_gamma` | REAL | Net gamma exposure at strike |
| `net_delta` | REAL | Net delta exposure at strike |
| `net_vanna` | REAL | Net vanna exposure at strike |
| `net_charm` | REAL | Net charm exposure at strike |
| `abs_gex_total` | REAL | Absolute gamma (|call| + |put|) |
| `date` | TEXT | Date string (YYYY-MM-DD) |

### `centroid_data` Table
Stores volume-weighted centroid positions:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `ticker` | TEXT | Ticker symbol |
| `timestamp` | INTEGER | Unix timestamp (5-min intervals) |
| `price` | REAL | Spot price |
| `call_centroid` | REAL | Volume-weighted avg call strike |
| `put_centroid` | REAL | Volume-weighted avg put strike |
| `call_volume` | INTEGER | Total call volume |
| `put_volume` | INTEGER | Total put volume |
| `date` | TEXT | Date string (YYYY-MM-DD) |

**Data Retention:**
- Automatic cleanup runs daily at midnight ET
- Only current day's data is retained
- Historical data can be exported before cleanup if needed

---

## 🔧 Troubleshooting

### Common Issues

#### **"Schwab API client not initialized" Error**
**Cause:** Missing or incorrect environment variables
**Solution:**
1. Verify `.env` file exists in project root
2. Check that all three variables are set correctly
3. Ensure no extra spaces around `=` signs
4. Restart the application after making changes

#### **OAuth Authentication Fails**
**Cause:** Callback URL mismatch
**Solution:**
1. Verify callback URL in `.env` matches Schwab Developer Portal exactly
2. Check for `http` vs `https` mismatch
3. Ensure port number matches (default: 5001)
4. Clear browser cookies and try again

#### **No Options Data Returned**
**Cause:** Invalid ticker or no options available
**Solution:**
1. Verify ticker symbol is correct and tradable
2. Check that options exist for that ticker
3. Try a known liquid ticker like SPY or AAPL
4. Ensure market is open or use recent market hours

#### **Charts Not Updating**
**Cause:** JavaScript error or network issue
**Solution:**
1. Open browser developer console (F12) to check for errors
2. Verify network connectivity
3. Check Schwab API status
4. Refresh the page
5. Clear browser cache

#### **Database Errors**
**Cause:** Corrupted database or permission issues
**Solution:**
1. Delete `options_data.db` file to reset database
2. Check file permissions in project directory
3. Restart application to reinitialize database

#### **Slow Performance**
**Cause:** Large options chains or too many expiration dates
**Solution:**
1. Reduce strike range percentage
2. Select fewer expiration dates
3. Use volume weighting instead of open interest (faster calculation)
4. Close unnecessary popout windows

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

### Feature Requests
- Additional Greek calculations (Rho, Veta, etc.)
- Export functionality for charts and data
- Custom alerts for exposure thresholds
- Multi-asset portfolio view
- Options strategy simulator

### Technical Improvements
- WebSocket implementation for true real-time streaming
- Caching layer for API responses
- Database optimization for larger datasets
- Mobile-responsive design improvements
- Unit tests and CI/CD pipeline

### Documentation
- Video tutorials
- Trading strategy guides
- API reference documentation

**To contribute:**
1. Fork the repository
2. Create a feature branch
3. Implement your changes with clear commit messages
4. Submit a pull request with detailed description

---

## 📚 Educational Resources

### Understanding Options Greeks
- [Options Greeks Explained](https://www.investopedia.com/trading/using-the-greeks-to-understand-options/) - Comprehensive guide to delta, gamma, theta, vega
- [Gamma Exposure & Market Making](https://squeezemetrics.com/monitor/download/pdf/white_paper.pdf) - SqueezeMetrics white paper on gamma exposure

### Market Microstructure
- **Dealer Hedging** - How market makers dynamically hedge their options books
- **Pin Risk** - Understanding why price gravitates toward high-gamma strikes
- **Volatility Surface** - How implied volatility varies across strikes and expirations

### Recommended Reading
- *Options as a Strategic Investment* by Lawrence McMillan
- *Option Volatility & Pricing* by Sheldon Natenberg
- *Dynamic Hedging* by Nassim Taleb

---

## 📜 License

This project is released under the **MIT License** - see LICENSE file for details.

**Educational and Personal Use Only:** This software is intended for educational purposes and personal trading analysis. It is not intended for commercial redistribution.

**Schwab API Terms:** Users must comply with [Schwab's API Terms of Service](https://developer.schwab.com/terms-of-service) and all applicable securities regulations.

---

## ⚠️ Disclaimer

**IMPORTANT: READ CAREFULLY BEFORE USE**

This software is provided "as is" for **informational and educational purposes only**. It does not constitute:
- Financial advice or recommendations
- Investment advice or solicitation
- Trading signals or guarantees

**Trading Risks:**
- Options trading involves **substantial risk** and is not suitable for all investors
- You can **lose more than your initial investment** with certain options strategies
- Past performance is not indicative of future results
- Greeks and exposures are **theoretical models** and may not reflect actual market behavior
- Market maker positioning is estimated and may not represent actual dealer positions

**No Warranty:**
- Calculations may contain errors or inaccuracies
- Data may be delayed, incorrect, or incomplete
- The software may fail or produce incorrect results
- No guarantee of uptime, accuracy, or reliability

**User Responsibility:**
- You are solely responsible for your trading decisions
- Always verify data from multiple sources
- Consult a qualified financial advisor before trading options
- Never risk more than you can afford to lose
- Understand the instruments you are trading before using them

**Regulatory Compliance:**
- This tool does not provide regulatory-compliant recordkeeping
- Users must maintain their own trading records
- Comply with all local, state, and federal regulations

**By using this software, you acknowledge and accept these risks and disclaimers.**

---

## 💬 Support & Community

### Get Help
- **Issues**: Report bugs via [GitHub Issues](https://github.com/EazyDuz1t/EzOptions-Schwab/issues)
- **Documentation**: Check this README and code comments
- **Schwab API**: [Schwab Developer Docs](https://developer.schwab.com/products/trader-api--individual)

### Contact
- **Discord**: eazy101
- **GitHub**: [@EazyDuz1t](https://github.com/EazyDuz1t)

### Acknowledgments
- **Schwab API** - For providing free market data access
- **Plotly** - For powerful open-source charting
- **Python Community** - For excellent scientific computing libraries

---

## 🔄 Version History

### Latest Features (Current Branch: multi-tab)
- ✅ Multi-ticker support with MARKET aggregation modes
- ✅ Volume-weighted centroid tracking
- ✅ Historical bubble level visualization
- ✅ Fullscreen and popout window functionality
- ✅ Delta-adjusted exposure calculations
- ✅ Third-order Greeks (Charm, Speed, Vomma, Color)
- ✅ Absolute GEX area chart overlay
- ✅ Customizable color intensity modes
- ✅ Persistent settings across sessions
- ✅ Real-time 1-second streaming updates

### Recent Commits
- `2a61908` - Added test and description
- `be048da` - Remove perspective parameter from exposures
- `c64080f` - Add fullscreen and popout functionality
- `1a94778` - Load settings on startup
- `e16cc93` - Update market ticker

---

**Built with ❤️ for options traders by traders**

*EzOptions-Schwab - Bringing institutional-grade options analytics to retail traders*