// README / HACS images (rendered by tools/render.mjs).
import { slide, banner } from './brand.mjs';
const body = `<span style="font-family:system-ui;font-weight:700;font-size:24px">Office</span>   <span style="font-family:system-ui;color:#5d6762">Wednesday 23 December 2026</span>

Working day today          <span style="color:#2f7d5b">On</span>
Working day tomorrow       Off   Christmas Eve (public holiday)
Today                      Working day
Next day off               24.12.2026   break 24.12 – 28.12, 5 days
Next working day           29.12.2026
Holidays and days off      Christmas Eve · Christmas · Second day of Christmas
                           Day off for Christmas, second day (26.12) → Mon 28.12`;
export default [
  { out: 'listing/entities-1280x720.png', width: 1280, height: 720, html: slide(1280, 720, { kicker: 'Home Assistant entities', title: 'Bulgarian working days, holidays and moved days off', body }) },
  { out: 'listing/social-preview-1280x640.png', width: 1280, height: 640, html: banner(1280, 640, { name: 'Sedmitsa Lite', tagline: 'Bulgarian working days and holidays for Home Assistant, computed locally.', chips: ['Labour Code holidays', 'Moved days off', 'Calendar', 'No cloud'], glyph: '7', kicker: 'Free Home Assistant integration' }) }
];
