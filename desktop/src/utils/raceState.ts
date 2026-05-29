import type { DriverStanding, RaceStateData } from "../types/bridge";

export function findPlayerStanding(
  raceState: RaceStateData | null,
): DriverStanding | null {
  if (!raceState) {
    return null;
  }
  const carIdx = raceState.player.car_idx;
  if (carIdx == null) {
    return null;
  }
  return (
    raceState.standings.drivers.find((driver) => driver.car_idx === carIdx) ??
    null
  );
}
