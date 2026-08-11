/**
 * Welcome 登入前頁 · 黑白水點落下＋不規則墨斑散開（LOCKED-v1）
 */
import '@/styles/welcome-ink.css';

type DropShape = {
  dw: string;
  dh: string;
  br: string;
  dop: string;
  dblur: string;
  bscale: number;
};

type StainSpec = {
  sw: string;
  sh: string;
  ox: string;
  oy: string;
  sbr: string;
  srot: string;
  sblur: string;
  speak: string;
  speakScale: number;
  sendScale: number;
  sg: string;
};

type InkEvent = {
  left: string;
  land: string;
  dur: string;
  delay: string;
};

const SHAPES: DropShape[] = [
  { dw: '16px', dh: '22px', br: '50% 50% 48% 48% / 48% 48% 52% 52%', dop: '0.72', dblur: '0.35px', bscale: 1.25 },
  { dw: '11px', dh: '18px', br: '50% 50% 45% 45% / 55% 55% 45% 45%', dop: '0.78', dblur: '0.25px', bscale: 1 },
  { dw: '6px', dh: '20px', br: '40% 40% 50% 50% / 30% 30% 70% 70%', dop: '0.65', dblur: '0.2px', bscale: 0.75 },
  { dw: '8px', dh: '12px', br: '50%', dop: '0.7', dblur: '0.3px', bscale: 0.85 },
  { dw: '7px', dh: '26px', br: '45% 45% 50% 50% / 25% 25% 75% 75%', dop: '0.6', dblur: '0.15px', bscale: 0.7 },
  { dw: '14px', dh: '17px', br: '48% 52% 50% 50% / 50% 50% 50% 50%', dop: '0.75', dblur: '0.4px', bscale: 1.15 },
  { dw: '5px', dh: '14px', br: '50% 50% 45% 45% / 40% 40% 60% 60%', dop: '0.55', dblur: '0.2px', bscale: 0.65 },
  { dw: '13px', dh: '24px', br: '50% 50% 42% 42% / 58% 58% 42% 42%', dop: '0.8', dblur: '0.3px', bscale: 1.2 },
];

function stainSet(bscale: number): StainSpec[] {
  const s = bscale;
  return [
    {
      sw: `${Math.round(100 * s)}px`,
      sh: `${Math.round(86 * s)}px`,
      ox: `${Math.round(-8 * s)}px`,
      oy: `${Math.round(4 * s)}px`,
      sbr: '38% 62% 48% 52% / 55% 40% 60% 45%',
      srot: '-12deg',
      sblur: '8px',
      speak: '0.5',
      speakScale: 2.6 * s,
      sendScale: 4.4 * s,
      sg: 'radial-gradient(ellipse 70% 60% at 40% 42%, rgba(50,50,50,0.28) 0%, rgba(80,80,80,0.1) 45%, transparent 72%)',
    },
    {
      sw: `${Math.round(70 * s)}px`,
      sh: `${Math.round(95 * s)}px`,
      ox: `${Math.round(28 * s)}px`,
      oy: `${Math.round(-18 * s)}px`,
      sbr: '60% 40% 55% 45% / 35% 65% 40% 60%',
      srot: '18deg',
      sblur: '9px',
      speak: '0.38',
      speakScale: 2.2 * s,
      sendScale: 3.8 * s,
      sg: 'radial-gradient(ellipse 55% 75% at 60% 35%, rgba(40,40,40,0.22) 0%, transparent 68%)',
    },
    {
      sw: `${Math.round(55 * s)}px`,
      sh: `${Math.round(48 * s)}px`,
      ox: `${Math.round(-36 * s)}px`,
      oy: `${Math.round(-22 * s)}px`,
      sbr: '45% 55% 70% 30% / 50% 45% 55% 50%',
      srot: '-28deg',
      sblur: '6px',
      speak: '0.32',
      speakScale: 2.0 * s,
      sendScale: 3.4 * s,
      sg: 'radial-gradient(circle at 30% 60%, rgba(35,35,35,0.2) 0%, transparent 65%)',
    },
    {
      sw: `${Math.round(48 * s)}px`,
      sh: `${Math.round(62 * s)}px`,
      ox: `${Math.round(22 * s)}px`,
      oy: `${Math.round(30 * s)}px`,
      sbr: '70% 30% 40% 60% / 45% 55% 48% 52%',
      srot: '32deg',
      sblur: '7px',
      speak: '0.28',
      speakScale: 1.9 * s,
      sendScale: 3.2 * s,
      sg: 'radial-gradient(ellipse 80% 50% at 55% 55%, rgba(45,45,45,0.18) 0%, transparent 70%)',
    },
    {
      sw: `${Math.round(36 * s)}px`,
      sh: `${Math.round(34 * s)}px`,
      ox: `${Math.round(-12 * s)}px`,
      oy: `${Math.round(38 * s)}px`,
      sbr: '52% 48% 45% 55% / 60% 40% 58% 42%',
      srot: '8deg',
      sblur: '5px',
      speak: '0.24',
      speakScale: 1.7 * s,
      sendScale: 2.9 * s,
      sg: 'radial-gradient(circle at 50% 40%, rgba(30,30,30,0.16) 0%, transparent 62%)',
    },
  ];
}

const INK_EVENTS: InkEvent[] = [
  { left: '16%', land: '56vh', dur: '5.6s', delay: '0s' },
  { left: '30%', land: '64vh', dur: '6.3s', delay: '0.55s' },
  { left: '46%', land: '50vh', dur: '5.2s', delay: '0.2s' },
  { left: '58%', land: '68vh', dur: '6.6s', delay: '1.05s' },
  { left: '72%', land: '54vh', dur: '5.7s', delay: '0.75s' },
  { left: '24%', land: '72vh', dur: '6.1s', delay: '1.5s' },
  { left: '64%', land: '46vh', dur: '5.4s', delay: '2.0s' },
  { left: '40%', land: '60vh', dur: '5.9s', delay: '2.45s' },
];

function parseDelaySeconds(delay: string): number {
  return parseFloat(delay.replace('s', '')) || 0;
}

export default function WelcomeInkBackground() {
  return (
    <div className="welcome-ink-field" aria-hidden="true">
      {INK_EVENTS.map((event, index) => {
        const shape = SHAPES[index % SHAPES.length];
        const stains = stainSet(shape.bscale * 1.5);
        const eventStyle = {
          left: event.left,
          ['--land' as string]: event.land,
          ['--fall' as string]: `calc(${event.land} + 12vh)`,
          ['--dur' as string]: event.dur,
          ['--delay' as string]: event.delay,
          ['--dw' as string]: shape.dw,
          ['--dh' as string]: shape.dh,
          ['--br' as string]: shape.br,
          ['--dop' as string]: shape.dop,
          ['--dblur' as string]: shape.dblur,
        };

        return (
          <div key={event.left + event.delay} className="welcome-ink-event" style={eventStyle}>
            <div className="welcome-ink-drop" />
            {stains.map((stain, stainIndex) => (
              <div
                key={stainIndex}
                className="welcome-ink-stain"
                style={{
                  ['--sw' as string]: stain.sw,
                  ['--sh' as string]: stain.sh,
                  ['--ox' as string]: stain.ox,
                  ['--oy' as string]: stain.oy,
                  ['--sbr' as string]: stain.sbr,
                  ['--srot' as string]: stain.srot,
                  ['--sblur' as string]: stain.sblur,
                  ['--speak' as string]: stain.speak,
                  ['--speak-scale' as string]: String(stain.speakScale),
                  ['--send-scale' as string]: String(stain.sendScale),
                  ['--sg' as string]: stain.sg,
                  ['--dur' as string]: event.dur,
                  ['--land' as string]: event.land,
                  ['--stain-delay' as string]: `${parseDelaySeconds(event.delay) + stainIndex * 0.035}s`,
                }}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
}
