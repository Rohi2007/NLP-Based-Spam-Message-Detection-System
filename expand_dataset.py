"""
expand_dataset.py
─────────────────
Appends a large batch of labelled spam/ham messages to the existing
spam_dataset.csv, deduplicates, and saves.

Categories covered:
  SPAM : prize/lottery, phishing, OTP fraud, loan scam, job scam,
         crypto scam, adult spam, insurance fraud, delivery scam,
         threatening/extortion, fake govt notices, shopping deals
  HAM  : casual chat, work/office, family, appointments, news,
         reminders, study/college, delivery confirmations, banking
         legit, social plans
"""

import os
import pandas as pd

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "spam_dataset.csv")

# ─── New SPAM samples ─────────────────────────────────────────────────────────
new_spam = [
    # ── Prize / Lottery ──
    "Congratulations! You've been selected as a lucky winner of $10,000 cash. Call 1-800-WIN-NOW to claim.",
    "You have WON our monthly draw! Claim your Rs. 50,000 prize by replying WIN to this number.",
    "WINNER ALERT: Your phone number won a $500 Amazon Gift Card. Click http://amzn-giveaway.xyz now!",
    "You are today's lucky winner! Collect your FREE iPad Pro. Visit http://claimnow.win/ipad immediately.",
    "Jackpot! Your entry has won $25,000 in our lottery. Send your bank details to collect.",
    "You've been randomly selected to receive a CASH REWARD of 1,00,000 rupees! Reply CLAIM.",
    "Lottery commission notifies you: Your ticket #A4728 has WON. Call 0800-123-456 in 24 hours.",
    "Free entry into our $1,000,000 draw just for being our customer! Text WIN to 88888 now.",
    "Congratulations you have just been awarded a HOLIDAY GIFT. Visit http://holiday-prize.co/claim.",
    "Your number has been drawn in our VIP lottery. You won 75,000 rupees. Claim at http://win.fast.xyz",
    "Lucky you! Your mobile was picked in our grand prize draw. Get your $2000 voucher: http://prizes.click",
    "FINAL NOTICE: Unclaimed prize of Rs.1,20,000 will expire tonight. Call now 09812345678.",

    # ── Phishing / Account Fraud ──
    "Your SBI account has been SUSPENDED due to unusual activity. Verify immediately: http://sbi-secure.xyz",
    "ALERT: Your PayPal account is limited. Restore access now: http://paypal-verify.ru/login",
    "HDFC Bank: Your net banking has been blocked. Click to unlock: http://hdfc-netbk.cc",
    "Your Amazon account will be closed in 24 hours. Confirm your identity: http://amzn-id.xyz",
    "Dear customer, your Aadhar KYC is pending. Update now to avoid deactivation: http://uidai-kyc.ga",
    "ICICI Bank: Unusual login from New Delhi. If not you, secure account: http://icici-block.xyz/secure",
    "Your Netflix subscription failed. Update payment info: http://netflix-billing.ru/update",
    "Google Alert: New sign-in from unknown device. Secure your account: http://google-security.xyz",
    "URGENT Apple ID locked. Verify at: http://apple-id-restore.info or lose access permanently.",
    "Govt of India: Your PAN card is suspended. Update KYC at http://incometax-pan.ga within 48 hrs.",
    "Dear User, Your EPF account has an issue. Log in at http://epfonline.in-verify.com to fix now.",
    "Your Flipkart wallet Rs.499 cashback pending. Claim here: http://flipkart-cashbk.xyz/claim",

    # ── OTP / SIM Fraud ──
    "Do not share this OTP with anyone. Your BANK OTP is 847219. We will NEVER ask for it.",
    "Your OTP for SIM porting is 921847. Share it with our agent to complete the process.",
    "SECURITY CODE 558821. Our executive needs this to process your loan. Share immediately.",
    "Your account verification OTP is 334892. Required by our KYC team — share now to proceed.",
    "Hi, I'm calling from Airtel. Your number is being upgraded. Please share the OTP you just received.",

    # ── Loan / Financial Scam ──
    "Get instant personal loan of Rs.5,00,000 with NO documents in 10 minutes! Apply: http://fastloan.xyz",
    "Pre-approved loan offer: Rs.2 lakh at 0% interest! Limited time. WhatsApp 9898123456 now.",
    "Dear Customer, you are eligible for instant cash of Rs.50,000. Minimal documents. Call 1800-LOAN.",
    "Loan approved! Rs.1,00,000 credit in your account. Pay small processing fee of Rs.999 first.",
    "Work from home & earn Rs.5000/day! No investment. Limited slots. Join now: http://earnfast.biz",
    "Earn Rs.10,000 daily from your mobile! Secret investment method. 100% guaranteed profit. Click here.",
    "CRYPTO PROFIT ALERT: Our bot earned $5200 this week. Join for free: http://cryptobot.earn.xyz",
    "Investment plan: Put in $500, earn $5000 in 7 days. Guaranteed returns. WhatsApp +1-555-INVEST.",
    "Debt consolidation: Clear all your loans in ONE payment. Call 0800-DEBT-FREE for a free quote.",
    "Quick payday loan: Get £500 in your account in 1 hour. No credit check. Text LOAN to 60060.",

    # ── Job Scam ──
    "JOB ALERT: Earn Rs.35,000/month working from home. No experience needed. Apply now: http://jobs.easy.in",
    "Urgent hiring: Data entry operator. Salary 25k/month. Work from home. Pay Rs.500 registration: http://hjobs.biz",
    "Part-time job offer: Rs.15,000 per week for 2 hours daily. Limited slots. WhatsApp 9912345678.",
    "Google hiring work-from-home employees. Salary $3000/month. Apply at http://google-wfh-jobs.xyz",
    "Amazon is hiring home-based workers! Earn $500/week. No experience needed. Click: http://amzn.jobs.xyz",
    "We saw your resume on Naukri. Salary up to 8 LPA. Pay Rs.1200 for joining kit. Confirm now.",

    # ── Delivery / Package Scam ──
    "USPS: Your parcel #US748271 is on hold. Pay $2.99 customs fee at: http://usps-delivery.xyz",
    "FedEx Notice: Package could not be delivered. Reschedule here: http://fedex-redeliver.cc",
    "Amazon: Your package is delayed. Update your delivery address: http://amzn-delivery.ru/track",
    "DHL Alert: Your shipment is held at customs. Pay release fee of Rs.299: http://dhl-customs.biz",
    "India Post: Your Speed Post #IN129388 awaits pickup. Confirm address: http://indiapost-track.ga",
    "COURIER NOTICE: Parcel returned to sender. Click to reattempt: http://courier-retry.xyz/rebook",

    # ── Threatening / Extortion ──
    "We have hacked your device and recorded you. Pay $1500 in Bitcoin or we release the footage.",
    "Your computer has been compromised. Transfer $500 in gift cards within 24 hours or files deleted.",
    "I have installed malware on your phone. Pay Rs.50,000 or your contacts will receive your photos.",
    "This is your final warning. Pay $2000 or your information goes public. Reply to negotiate.",
    "Police cyber cell: You accessed illegal content. Pay fine of Rs.10,000 to avoid arrest. Call now.",

    # ── Insurance / Health Scam ──
    "FREE health insurance for 1 year! Just pay Rs.299 activation fee. Limited offer. Call 1800-HEALTH.",
    "Your car insurance expires soon. Renew NOW and save 50%! Click: http://insurance-renew.xyz",
    "Claim your unclaimed insurance of Rs.2,50,000. Policy no. LI-887291. Contact 9911223344 today.",
    "COVID relief fund: Rs.5000 per person from Govt of India. Apply at http://relief-fund.ga now.",
    "You are eligible for a FREE medical check-up worth Rs.3000. Book your slot: http://freehealth.biz",

    # ── Adult / Subscription Spam ──
    "You have been subscribed to HOT content @ Rs.150/day. To unsubscribe text STOP to 55555.",
    "Meet singles in your area tonight! 100% free. Click http://meetlocal.xyz — no strings attached.",
    "Your FREE trial of VideoXXX expires today. Continue membership: http://adult-vids.xyz/continue",
    "Get unlimited adult content for just $9.99/month. 1000s of videos. Join: http://unlimitedxx.com",

    # ── Fake Shopping / Cashback ──
    "Meesho: Earn Rs.500 cashback on your next order. Activate offer: http://meesho-cashbk.xyz",
    "Exclusive deal: iPhone 15 for only Rs.4999! Limited stock. Order NOW: http://cheap-iphones.biz",
    "SALE ALERT: 90% OFF on all items today only! Shop before midnight: http://bigsale.xyz/today",
    "Congratulations Paytm user! Rs.2000 cashback credited. Claim before expiry: http://paytm-offer.ga",
    "Your Google Pay reward of Rs.1500 is ready. Claim now before it expires: http://gpay-bonus.cc",
    "Win a brand new Samsung TV! Answer 3 questions: http://samsung-quiz.xyz. Only 5 left!",
    "BOGO OFFER: Buy 1 get 2 FREE on all products! Code: FREEGIFT. Shop at http://bogo-deals.xyz",

    # ── Fake Government / Legal ──
    "Income Tax Dept: You have an unclaimed tax refund of Rs.18,500. Update bank details immediately.",
    "TRAI: Your mobile number will be blocked in 2 hours due to misuse. Contact 198 now.",
    "This is an automated message from IRS. Arrest warrant issued in your name. Call 1-800-829-IRS.",
    "Electricity dept: Your power will be cut in 30 minutes. Pay Rs.1,200 now: http://ebill-pay.xyz",
    "Your driving license has been flagged. Pay Rs.500 fine online to avoid suspension: http://rto.ga",
    "RBI notification: Your KYC needs updating. Failure to comply will freeze your account. Click here.",

    # ── Crypto / Investment ──
    "BITCOIN INVESTMENT: Turn $100 into $5000 in 30 days! Proven strategy. Join: http://cryptogains.xyz",
    "Elon Musk Bitcoin giveaway: Send 0.1 BTC and get 0.2 BTC back! Visit http://elon-btc-give.xyz",
    "NFT drop alert: FREE NFTs for first 1000 sign-ups! Mint now: http://nft-free-mint.xyz",
    "TRADING BOT: 300% returns guaranteed in 7 days. Start with as little as $50. Signal group join.",
    "Exclusive forex signals: 95% accuracy! Join our premium Telegram group. First month FREE.",

    # ── Generic urgent/offer ──
    "ACT NOW: Your exclusive offer expires in 1 hour. Don't miss this limited-time deal!",
    "Special member discount: 70% OFF for the next 30 minutes. Use code VIP70 at checkout.",
    "LAST CHANCE: Redeem your reward points before they expire tonight. Click to claim!",
    "You have unused reward points worth Rs.3200. Redeem before 11:59 PM tonight.",
    "OFFER ENDING SOON: Buy any product and get FREE gift. Limited stock. Order now!",
    "Earn 500 bonus miles just for clicking this link. No purchase required. Click now.",
    "Your FREE subscription to our premium service starts today. No credit card needed. Sign up!",
    "URGENT: Complete your survey and win a Rs.5000 voucher. Only 3 spots left!",
]

# ─── New HAM samples ──────────────────────────────────────────────────────────
new_ham = [
    # ── Casual Chat ──
    "Hey! What are you up to this weekend? Thinking of catching a movie.",
    "Did you see the cricket match last night? What a finish!",
    "Can we reschedule our call to 4 PM? I have a conflict at 3.",
    "Just wanted to check in — how are you feeling after the exam?",
    "Hey, the wifi password at the café is CoffeeShop2024. Come join us!",
    "Happy birthday! Hope you have an amazing day 🎂",
    "Sorry I missed your call. I was in a meeting. Will ring you back in 10.",
    "Are you free for lunch today? There's a new place near the office.",
    "I left my charger at your place. Can you bring it tomorrow?",
    "Just landed in Bangalore. Let's meet up this week!",
    "The movie was so good! We should go again next Friday.",
    "I'll be 15 minutes late. Please order for me — you know what I like.",
    "What's the dress code for Saturday's event?",
    "Thanks for covering my shift. I owe you one!",
    "Did you get the notes from today's class? I had to leave early.",
    "Hey, can you water my plants while I'm away? Spare key is under the mat.",
    "Congrats on the promotion! Knew you'd get it. Dinner is on me!",
    "The code review is done. Pushed my changes to the dev branch.",
    "I'm at the grocery store. Do we need anything else?",
    "Kids are asking if you're coming for dinner on Sunday. Let me know!",

    # ── Work / Office ──
    "Hi, please review the proposal and share feedback by EOD.",
    "Team standup moved to 10:30 AM tomorrow. Please update your calendars.",
    "The client presentation is on Thursday at 2 PM. Please be ready.",
    "Can you please send me the updated Q3 report when you get a chance?",
    "I've shared the meeting notes on Confluence. Please review and add comments.",
    "Your leave request for Oct 15–17 has been approved. Enjoy your break!",
    "Please complete the mandatory cybersecurity training by Friday.",
    "Reminder: Performance review forms due by end of this month.",
    "The Jenkins build failed on PR #245. Please check the logs.",
    "New ticket assigned to you: Bug #1823 — Login page crash on iOS. Priority: High.",
    "Project kickoff call scheduled for Monday 9 AM. Agenda sent via email.",
    "Could you look into the production issue? Users reporting slowness since 2 PM.",
    "The API documentation has been updated. Please sync your local copy.",
    "HR: Please submit your investment declarations by 31st October.",
    "Your onboarding buddy is Priya Sharma. She'll reach out to you Monday.",
    "Office will be closed on Friday for Diwali. Enjoy the long weekend!",
    "Please confirm your attendance for the team offsite on Nov 12–13.",
    "Your work laptop is ready for pickup from IT. Carry your ID.",

    # ── Family / Personal ──
    "Mom says dinner is at 7 PM. Please don't be late.",
    "Dad's flight lands at 9:15 PM at T2. Can you pick him up?",
    "The plumber is coming tomorrow between 10 and 12. Can you be home?",
    "We're running low on milk and eggs. Can you grab some on the way?",
    "Aunty's birthday is next Sunday. Should we get a cake?",
    "The school called — Rohan has a fever. Can you pick him up?",
    "The electricity bill is due tomorrow. Don't forget to pay.",
    "Your driving license renewal appointment is on the 18th at 11 AM.",
    "I've booked the hotel in Goa. Check-in is on the 25th. Details sent.",
    "The washing machine repair guy is coming at 3 PM today.",

    # ── Appointments / Reminders ──
    "Reminder: Your dentist appointment is tomorrow at 11:30 AM.",
    "Dr. Sharma's office: Your blood test results are ready. Please collect.",
    "Your car service is due. Book an appointment at the nearest service center.",
    "Reminder: EMI of Rs.4,500 due on the 5th. Ensure sufficient balance.",
    "Your passport is ready for collection at the regional office.",
    "Library reminder: Books due for return on 12th October.",
    "Your gym membership expires on October 31. Renew to keep your discount.",
    "Course enrollment deadline: Register for next semester by October 20.",
    "Reminder: Team lunch at 1 PM today at Mainland China. Don't miss it!",
    "Your annual health check-up is scheduled for 15th October at 9 AM.",

    # ── Legitimate Banking / Transactional ──
    "Your SBI account XXXX1234 was credited with Rs.25,000 on 04-Oct. Avail bal: Rs.42,318.",
    "UPI payment of Rs.500 to Swiggy on 04-Oct successful. Ref no: 123456789.",
    "Your HDFC credit card bill of Rs.7,842 is due on Oct 15. Pay to avoid interest.",
    "ATM withdrawal of Rs.2,000 from ICICI Bank ATM MG Road at 3:42 PM.",
    "Your fixed deposit of Rs.1,00,000 has matured. Please visit the branch to renew.",
    "OTP for your SBI net banking login is 483920. Valid for 5 minutes. Do not share.",
    "Your insurance premium of Rs.12,000 is due on Oct 20. Pay via NetBanking or UPI.",
    "Axis Bank: Your cheque no. 005821 for Rs.15,000 has been cleared.",
    "NEFT of Rs.35,000 sent to Rahul Verma successful. Ref: NEFTIN9382847.",
    "Your loan account EMI of Rs.8,243 has been auto-debited on Oct 5.",

    # ── Delivery Confirmations (Legit) ──
    "Your Flipkart order #FL-28374 has been shipped. Expected delivery: Oct 7.",
    "Swiggy: Your order from Domino's is out for delivery. ETA: 20 minutes.",
    "Amazon: Package delivered to your doorstep on Oct 4 at 2:15 PM.",
    "Zomato: Your order is confirmed. Priya's Kitchen is preparing your food.",
    "Nykaa: Order #NK-99281 dispatched via Delhivery. Track: http://delhivery.com/track",
    "Meesho: Your return has been picked up. Refund will be processed in 5-7 days.",
    "Your Zepto order is arriving in 10 minutes. Get ready to receive.",

    # ── Study / College ──
    "Reminder: Assignment submission deadline is Friday midnight. Late submissions not accepted.",
    "Prof. Sharma has rescheduled Monday's lecture to Tuesday 2 PM. Venue same.",
    "Results for mid-sem exams are out on the student portal. Check your scores.",
    "Library issue: The reference books you requested are now available for issue.",
    "Your project viva is scheduled for Oct 22 at 10 AM. Panel will be announced.",
    "Attendance report: You have 82% attendance this month. Maintain above 75%.",
    "Today's NLP class is cancelled. Extra class on Saturday at 9 AM instead.",
    "Hackathon registration closes tomorrow. Team of 2-4. Register on the portal.",
    "Placement drive by TCS on Oct 28. Eligible branches: CSE, IT, ECE. Register now.",
    "College fest registrations open! Events include coding, debate, and cultural. Join now.",

    # ── Social / Plans ──
    "We're planning a trip to Manali in December. Are you in?",
    "Game night at my place on Saturday. Bring snacks!",
    "The reunion is confirmed for Nov 5 at Hotel Radisson. RSVP by Oct 25.",
    "Book your tickets for the concert. Last few remaining — don't miss it!",
    "Dinner plans changed to 8 PM. The table is booked at The Spice Route.",
    "We're doing a potluck. I'll bring pasta. What can you bring?",
    "Morning run at 6 AM tomorrow — Cubbon Park. Join if you can!",
    "Movie night tonight. Vote for your pick in the group: Inception or Interstellar?",
    "I'm at the airport. Flight delayed by 2 hours. Will keep you posted.",
    "Just booked the badminton court for Sunday 7 AM. See you there!",

    # ── News / Info ──
    "Today's weather: Heavy rain expected in the evening. Carry an umbrella.",
    "Traffic alert: Major roadblock on ORR due to waterlogging. Take alternate route.",
    "Power shutdown in your area tomorrow 9 AM–1 PM for maintenance. Plan accordingly.",
    "COVID booster camp at Community Hall tomorrow 10 AM–4 PM. Bring your vaccination card.",
    "New park opening ceremony at 5 PM today near the railway station.",
    "Scheduled water supply disruption on Oct 6. Store water today.",
    "Voting day on Oct 15 is a public holiday. Use your vote responsibly.",
]

# ─── Load existing + append ───────────────────────────────────────────────────
df_existing = pd.read_csv(DATA_PATH)
print(f"Existing: {len(df_existing)} rows  (spam={( df_existing.label=='spam').sum()}, ham={(df_existing.label=='ham').sum()})")

spam_rows = pd.DataFrame({"label": "spam", "message": new_spam})
ham_rows  = pd.DataFrame({"label": "ham",  "message": new_ham })

df_new = pd.concat([df_existing, spam_rows, ham_rows], ignore_index=True)

# Deduplicate on message text (strip whitespace)
df_new["message"] = df_new["message"].str.strip()
before = len(df_new)
df_new = df_new.drop_duplicates(subset="message")
print(f"Dropped {before - len(df_new)} duplicates")

df_new.to_csv(DATA_PATH, index=False)
print(f"Saved   : {len(df_new)} rows  (spam={(df_new.label=='spam').sum()}, ham={(df_new.label=='ham').sum()})")
