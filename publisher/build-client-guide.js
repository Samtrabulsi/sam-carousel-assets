/**
 * Build the GHL Social Publisher Client Setup Guide (.docx).
 * Run from /Users/samtrabulsi/Downloads/carousel-system:
 *   node publisher/build-client-guide.js
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, LevelFormat,
  ExternalHyperlink, TabStopType, TabStopPosition,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageNumber, PageBreak,
} = require("docx");

// ----- helpers ---------------------------------------------------------

const BRAND = {
  primary:    "C17A5A",
  primaryDk:  "8B4A2A",
  ink:        "1C1410",
  inkSoft:    "555555",
  paper:      "F5EDE8",
  paperBd:    "EDE0D8",
  warn:       "B8421C",
  warnBg:     "FBE9E0",
  info:       "0F4C5C",
  infoBg:     "DCEEF2",
  rule:       "CCCCCC",
};

const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: BRAND.rule };
const tableBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder, insideHorizontal: thinBorder, insideVertical: thinBorder };

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80, line: 300 },
    children: [new TextRun({ text, ...opts })],
  });
}
function pRich(runs, paraOpts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80, line: 300 },
    ...paraOpts,
    children: runs,
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    pageBreakBefore: true,
    children: [new TextRun({ text })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text })],
  });
}
function bullet(text, runOpts = {}) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40, line: 280 },
    children: [new TextRun({ text, ...runOpts })],
  });
}
function nested(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 1 },
    spacing: { before: 30, after: 30, line: 280 },
    children: [new TextRun({ text })],
  });
}
function step(text) {
  return new Paragraph({
    numbering: { reference: "steps", level: 0 },
    spacing: { before: 100, after: 60, line: 300 },
    children: [new TextRun({ text })],
  });
}
function stepRich(runs) {
  return new Paragraph({
    numbering: { reference: "steps", level: 0 },
    spacing: { before: 100, after: 60, line: 300 },
    children: runs,
  });
}
function spacer(twips = 80) {
  return new Paragraph({ spacing: { before: twips, after: twips }, children: [new TextRun({ text: "" })] });
}
function mono(text) {
  return new TextRun({ text, font: "Courier New", size: 20 });
}

// Callout box: single-cell table, colored fill + left border
function callout({ title, body, kind = "warn" }) {
  const fill = kind === "warn" ? BRAND.warnBg : BRAND.infoBg;
  const accent = kind === "warn" ? BRAND.warn : BRAND.info;
  const heavy = { style: BorderStyle.SINGLE, size: 24, color: accent };
  const thin  = { style: BorderStyle.SINGLE, size: 4,  color: accent };
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: { top: thin, bottom: thin, left: heavy, right: thin },
            width: { size: 9360, type: WidthType.DXA },
            shading: { fill, type: ShadingType.CLEAR },
            margins: { top: 200, bottom: 200, left: 280, right: 240 },
            children: [
              new Paragraph({
                spacing: { after: 80 },
                children: [new TextRun({ text: title, bold: true, color: accent, size: 24 })],
              }),
              ...(Array.isArray(body) ? body : [body]).map((line) =>
                new Paragraph({
                  spacing: { before: 40, after: 40, line: 280 },
                  children: [new TextRun({ text: line, size: 22 })],
                }),
              ),
            ],
          }),
        ],
      }),
    ],
  });
}

// Simple two-column key/value table (for the troubleshooting section)
function kvTable(rows, headerLeft = "Issue", headerRight = "What to do") {
  const colLeft = 3800, colRight = 5560;
  const headFill = BRAND.paper;
  const headBd = { style: BorderStyle.SINGLE, size: 8, color: BRAND.primary };
  const rowBd  = { style: BorderStyle.SINGLE, size: 4, color: BRAND.rule };
  const headBorders = { top: headBd, bottom: headBd, left: thinBorder, right: thinBorder };
  const cellBorders = { top: rowBd, bottom: rowBd, left: rowBd, right: rowBd };
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [colLeft, colRight],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [
          new TableCell({
            borders: headBorders,
            width: { size: colLeft, type: WidthType.DXA },
            shading: { fill: headFill, type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 160, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: headerLeft, bold: true })] })],
          }),
          new TableCell({
            borders: headBorders,
            width: { size: colRight, type: WidthType.DXA },
            shading: { fill: headFill, type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 160, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: headerRight, bold: true })] })],
          }),
        ],
      }),
      ...rows.map(([l, r]) =>
        new TableRow({
          children: [
            new TableCell({
              borders: cellBorders,
              width: { size: colLeft, type: WidthType.DXA },
              margins: { top: 120, bottom: 120, left: 160, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: l })] })],
            }),
            new TableCell({
              borders: cellBorders,
              width: { size: colRight, type: WidthType.DXA },
              margins: { top: 120, bottom: 120, left: 160, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: r })] })],
            }),
          ],
        }),
      ),
    ],
  });
}

// Scopes table
function scopesTable(rows) {
  const colLeft = 4500, colRight = 4860;
  const headBd = { style: BorderStyle.SINGLE, size: 8, color: BRAND.primary };
  const rowBd  = { style: BorderStyle.SINGLE, size: 4, color: BRAND.rule };
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [colLeft, colRight],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [
          new TableCell({
            borders: { top: headBd, bottom: headBd, left: thinBorder, right: thinBorder },
            width: { size: colLeft, type: WidthType.DXA },
            shading: { fill: BRAND.paper, type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 160, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: "Scope name (paste exactly)", bold: true })] })],
          }),
          new TableCell({
            borders: { top: headBd, bottom: headBd, left: thinBorder, right: thinBorder },
            width: { size: colRight, type: WidthType.DXA },
            shading: { fill: BRAND.paper, type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 160, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: "Why we need it", bold: true })] })],
          }),
        ],
      }),
      ...rows.map(([scope, why]) =>
        new TableRow({
          children: [
            new TableCell({
              borders: { top: rowBd, bottom: rowBd, left: rowBd, right: rowBd },
              width: { size: colLeft, type: WidthType.DXA },
              margins: { top: 120, bottom: 120, left: 160, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: scope, font: "Courier New", size: 20 })] })],
            }),
            new TableCell({
              borders: { top: rowBd, bottom: rowBd, left: rowBd, right: rowBd },
              width: { size: colRight, type: WidthType.DXA },
              margins: { top: 120, bottom: 120, left: 160, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: why })] })],
            }),
          ],
        }),
      ),
    ],
  });
}

// ----- document content ------------------------------------------------

const cover = [
  spacer(2200),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
    children: [new TextRun({ text: "POSITIONING · BRAND VICTORY", size: 22, color: BRAND.primary, characterSpacing: 80 })],
  }),
  spacer(120),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 180 },
    children: [new TextRun({ text: "GHL Social Publisher", size: 56, bold: true, color: BRAND.ink })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 360 },
    children: [new TextRun({ text: "Client Setup Guide", size: 40, color: BRAND.primaryDk })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { top: { style: BorderStyle.SINGLE, size: 12, color: BRAND.primary, space: 4 } },
    spacing: { before: 320, after: 80 },
    children: [new TextRun({ text: "" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "Prepared by Sam Trabulsi", size: 26, color: BRAND.ink })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
    children: [new TextRun({ text: "Brand Victory · brandvictory.com", size: 22, color: BRAND.inkSoft })],
  }),
  spacer(4000),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Confidential — do not redistribute", size: 18, italics: true, color: BRAND.inkSoft })],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

const tocPage = [
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text: "Table of Contents" })],
  }),
  new TableOfContents("", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({ children: [new PageBreak()] }),
];

const section1 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "1. What this is and why we're asking" })] }),
  p("Your social media is being managed through an automated publishing system built on top of GoHighLevel (GHL). To schedule posts on your behalf — Facebook, Instagram, LinkedIn, X, and TikTok — we need a small set of read and write permissions on your GHL sub-account."),
  p("Rather than asking for your password (which would give us far more access than we need, and which we can't safely store), GHL gives us a cleaner option: a Private Integration Token (PIT). It's a single, narrowly-scoped key that you create, you control, and you can revoke at any time."),
  spacer(100),
  h2("What the token lets us do"),
  bullet("List the social media accounts you've connected in GHL — so we know which platforms to publish to."),
  bullet("Upload images and video to your GHL media library — the artwork attached to your posts."),
  bullet("Schedule posts in your Social Planner — appearing under your name on your platforms at the date and time we agree on."),
  bullet("Read back the scheduled queue — so we can confirm a post landed and show you what's coming up."),
  spacer(100),
  h2("What the token does NOT let us do"),
  bullet("It cannot log in as you on Facebook, Instagram, or any other platform directly."),
  bullet("It cannot read your contact lists, email content, payment information, or CRM data."),
  bullet("It cannot change your billing, your users, or your account settings."),
  bullet("It can be revoked instantly — one click in your GHL settings and our access stops."),
  spacer(120),
  callout({
    kind: "info",
    title: "TL;DR",
    body: [
      "You'll spend about 5 minutes creating a token in GHL, confirming your social accounts are connected, and sending the token + Location ID back to us.",
      "From then on, your posts get scheduled by us — you see them in your GHL planner and on your platforms when they publish.",
    ],
  }),
];

const section2 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "2. Create your Private Integration Token" })] }),
  p("Follow these steps inside GHL. Total time: about 3 minutes."),
  h2("Step-by-step"),
  step("Log in to GHL and switch to the sub-account you want managed. If you only have one sub-account, you're already there."),
  step("In the left sidebar, click Settings (gear icon at the bottom)."),
  step("In the Settings menu, look for Private Integrations. Depending on your GHL version, it may be near the bottom of the list or under a section called Business Profile or Integrations."),
  step("Click Create New Integration (or Add Integration)."),
  step("Name it: Brand Victory Publisher. The name is just a label for you — it can be anything that helps you recognize it later."),
  stepRich([
    new TextRun({ text: "Select the scopes listed below. " }),
    new TextRun({ text: "These are the only permissions we use — please don't grant more than this.", bold: true }),
  ]),
  spacer(120),
  scopesTable([
    ["locations.readonly", "Confirm we're connecting to the right sub-account."],
    ["users.readonly", "Identify the author for scheduled posts."],
    ["socialplanner/account.readonly", "List the social accounts (FB, IG, LinkedIn, etc.) you've connected."],
    ["socialplanner/post.readonly", "Read back the scheduled queue."],
    ["socialplanner/post.write", "Create the scheduled posts."],
    ["socialplanner/oauth.readonly", "Check whether your platform connections are still valid."],
    ["medias.readonly", "Read media library entries we've uploaded."],
    ["medias.write", "Upload post images and video to your media library."],
  ]),
  spacer(160),
  step("Click Create. GHL will display the token on screen exactly once — it looks like a long string starting with pit-…"),
  spacer(80),
  callout({
    kind: "warn",
    title: "⚠ Important — the token is shown only once",
    body: [
      "GHL will not show you this token again after you close the window. Copy it immediately to a secure place.",
      "If you lose it before sending it to us, that's fine — you can just delete the integration and create a new one. There's no penalty.",
    ],
  }),
  spacer(120),
  step("Find your Location ID. Look at the URL of any page inside this sub-account — it has this shape:"),
  pRich([
    mono("https://app.gohighlevel.com/v2/location/"),
    new TextRun({ text: "<YOUR-LOCATION-ID>", bold: true, font: "Courier New", size: 20 }),
    mono("/dashboard"),
  ]),
  p("The string between /location/ and the next slash is your Location ID. Copy it down. It looks like a random 20-character string."),
];

const section3 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "3. Confirm your social accounts are connected" })] }),
  p("The token only works for platforms you've actually connected inside GHL. Take a minute to check each one."),
  h2("How to check"),
  step("In the left sidebar, click Marketing → Social Planner."),
  step("At the top of the planner, click the Socials button (top right area)."),
  step("You'll see a list of all five platforms: Facebook, Instagram, LinkedIn, X (Twitter), and TikTok."),
  step("Each connected platform should show a green status or a profile picture. Disconnected or expired platforms show a red warning, a Reconnect button, or simply no account at all."),
  spacer(80),
  h2("If a platform is disconnected or expired"),
  p("Click Reconnect (or Add Account if it's never been connected). GHL will open a login window for that platform. Log in and authorize the connection. Each one takes about 30 seconds."),
  p("This step is worth doing now, even for platforms you're not sure you'll use — it costs nothing to leave a valid connection in place, and reconnecting later (after a token expires) is harder than reconnecting now."),
  spacer(120),
  callout({
    kind: "info",
    title: "Common gotcha",
    body: [
      "OAuth tokens on LinkedIn, X, and TikTok tend to expire every 60–90 days, even with no errors visible on your end.",
      "If you ever notice posts stop publishing on those platforms, the first thing to check is whether the connection lapsed. It's a one-minute fix.",
    ],
  }),
];

const section4 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "4. How to send us the token securely" })] }),
  p("The Private Integration Token is the only piece of sensitive data in this whole process. Please don't send it through any of these channels:"),
  bullet("Email (regular Gmail / Outlook). Email isn't encrypted in transit between systems."),
  bullet("SMS or unencrypted messaging."),
  bullet("Slack DMs in a workspace you don't own."),
  bullet("Public file-sharing links (Google Drive shared with 'anyone with the link', Dropbox public folders, etc.)."),
  spacer(120),
  h2("Recommended ways to send it"),
  step("1Password, Bitwarden, or LastPass shared item — preferred. Create a one-time secure share link and send that."),
  step("Signal, iMessage, or WhatsApp directly to Sam — encrypted end-to-end."),
  step("Send the token and the Location ID separately. Token in your password manager / encrypted channel, Location ID in any normal channel (it's not sensitive on its own)."),
  spacer(120),
  callout({
    kind: "warn",
    title: "⚠ Before you send",
    body: [
      "Double-check the token starts with pit- and is one long string (no line breaks, no quotation marks added by copy/paste).",
      "Once you send it, please don't paste it anywhere else — including your own notes. If you ever need to reference it, just create a new one and let us know.",
    ],
  }),
  spacer(120),
  h2("What we'll need from you in one message"),
  bullet("The Private Integration Token (sent via the secure channel above)."),
  bullet("Your Location ID (any channel — not sensitive)."),
  bullet("Your preferred publishing timezone, if it's not the same as the timezone in your GHL location settings (for example, Europe/Athens, America/New_York)."),
];

const section5 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "5. What happens after you hand it over" })] }),
  p("Once we receive your token and Location ID, here's what to expect:"),
  h2("Within 24 hours"),
  bullet("We run a one-time setup that confirms the token works, identifies your social accounts, and stores your configuration in our system."),
  bullet("You'll get a short confirmation from Sam: 'Setup complete. Here are the platforms we'll be publishing to: …' plus a flag for any disconnected platforms that need attention on your side."),
  spacer(80),
  h2("Ongoing"),
  bullet("Each scheduled post will appear in your GHL Social Planner before it publishes — you can see exactly what's queued, edit it, or cancel it yourself if you want to."),
  bullet("Posts publish to your platforms at the date and time we agreed on. They appear under your own profile or page — your followers see the post coming from you, not from us."),
  bullet("We'll send you a monthly summary of what was published and how it performed (optional — let us know if you'd rather not receive this)."),
  spacer(80),
  h2("If you ever want to pause or stop"),
  bullet("Go to Settings → Private Integrations in GHL and delete the integration named Brand Victory Publisher."),
  bullet("Our access stops instantly. No notice required, no penalty."),
  bullet("If you want to restart later, just create a new token and send it our way. The whole setup takes about 5 minutes again."),
  spacer(120),
  callout({
    kind: "info",
    title: "You stay in control",
    body: [
      "You can revoke this token at any time, for any reason, with one click in your GHL settings. We can't escalate access, we can't reattach a deleted token, and we can't see anything outside of the scopes you granted.",
      "Think of it as giving us a key that opens one specific door — and you keep the ability to change the lock whenever you want.",
    ],
  }),
];

const section6 = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "6. Troubleshooting" })] }),
  p("If you hit any of these along the way, here's how to handle it. None of these are unusual — they're all fixable in a couple of minutes."),
  spacer(120),
  kvTable([
    ["I can't find Private Integrations in Settings", "Your sub-account may have it under a slightly different menu. Try searching the Settings page for 'integration' or check under 'Business Profile' or 'API'. If still no luck, send Sam a screenshot of your Settings sidebar and we'll point you to it."],
    ["I closed the window before copying the token", "No problem. Go back to Private Integrations, delete the one you just created, and create a new one. There's no limit and no penalty."],
    ["GHL says one of the scopes doesn't exist", "Scope names occasionally change between GHL versions. Pick the closest match (e.g. 'socialplanner.account.readonly' vs 'socialplanner/account.readonly') — both work. If unsure, grant the closest one and we'll let you know if anything's missing."],
    ["The 'Reconnect' button on a platform just spins", "Pop-up blockers in your browser can swallow the OAuth window. Try disabling pop-up blockers for app.gohighlevel.com and clicking Reconnect again."],
    ["My LinkedIn / X / TikTok keeps expiring", "Normal — those platforms invalidate connections every 60–90 days for security. Just reconnect when prompted. Sam will flag it if a scheduled post fails because of an expired connection."],
    ["I want to see what's been scheduled", "Open Marketing → Social Planner inside GHL. Every post we've scheduled is visible there, with the date, content, and platforms. You can edit or cancel any of them yourself."],
    ["I want to revoke access entirely", "Settings → Private Integrations → click the integration named 'Brand Victory Publisher' → Delete. Done. Our access stops immediately."],
    ["Something else", "Send Sam a quick message — info@samtrabulsi.com or your usual channel. Include what you tried and a screenshot if you can. We'll respond same-day."],
  ]),
];

const closing = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "Closing notes" })] }),
  p("Thanks for taking the time to set this up. We try to keep onboarding under 15 minutes total — most clients are done in under 10."),
  p("Once your token reaches us, you don't need to touch this process again. Your only job from here on is the content itself: telling us what's coming up, what's worth amplifying, and what to skip."),
  spacer(120),
  h2("Quick recap"),
  bullet("Create a Private Integration Token in GHL with the 8 scopes listed in Section 2."),
  bullet("Confirm your 5 social accounts are connected (Section 3)."),
  bullet("Send the token via a secure channel + Location ID via any channel (Section 4)."),
  bullet("Wait for the confirmation from Sam — typically same-day."),
  spacer(200),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { top: { style: BorderStyle.SINGLE, size: 12, color: BRAND.primary, space: 8 } },
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text: "" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Questions?", size: 28, bold: true, color: BRAND.ink })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text: "Sam Trabulsi · info@samtrabulsi.com · brandvictory.com", size: 22, color: BRAND.inkSoft })],
  }),
];

// ----- build -----------------------------------------------------------

const doc = new Document({
  creator: "Sam Trabulsi · Brand Victory",
  title: "GHL Social Publisher — Client Setup Guide",
  description: "Hand-off setup guide for new clients onboarding to the GHL Social Publisher workflow.",
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: BRAND.ink },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: BRAND.primaryDk },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: BRAND.ink },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ],
      },
      {
        reference: "steps",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [new TextRun({ text: "GHL Social Publisher · Client Setup Guide", size: 18, color: BRAND.inkSoft })],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              tabStops: [{ type: TabStopType.RIGHT, position: 9360 }],
              children: [
                new TextRun({ text: "Brand Victory · Confidential", size: 18, color: BRAND.inkSoft }),
                new TextRun({ text: "\tPage " }),
                new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
                new TextRun({ text: " of " }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 }),
              ],
            }),
          ],
        }),
      },
      children: [
        ...cover,
        ...tocPage,
        ...section1,
        ...section2,
        ...section3,
        ...section4,
        ...section5,
        ...section6,
        ...closing,
      ],
    },
  ],
});

const outPath = path.join(__dirname, "GHL-Social-Publisher-Client-Setup-Guide.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outPath, buf);
  const kb = (buf.length / 1024).toFixed(1);
  console.log(`Wrote ${outPath}  (${kb} KB)`);
});
