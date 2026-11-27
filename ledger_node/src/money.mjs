/**
 * Integer-cents money helpers (never use floating-point arithmetic for currency).
 */

export function parseCents(raw) {
  if (!Number.isInteger(raw) || raw <= 0 || raw > 100_000_000) {
    throw new RangeError("amountCents must be a positive integer <= 100000000");
  }
  return raw;
}

export function formatUsd(cents) {
  const whole = Math.floor(cents / 100);
  const frac = String(cents % 100).padStart(2, "0");
  return `$${whole}.${frac}`;
}
