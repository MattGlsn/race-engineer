export type ConnectionState = {
  state: string;
  is_connected: boolean;
  sdk_initialized: boolean;
  sdk_connected: boolean;
};

export type GapSnapshot = {
  target_car_idx: number | null;
  gap_seconds: number | null;
  distance_meters: number | null;
};

export type PlayerPositionSnapshot = {
  car_idx: number | null;
  overall_position: number | null;
  class_position: number | null;
  field_size: number | null;
};

export type FuelConsumptionSnapshot = {
  last_lap: number | null;
  last_lap_usage: number | null;
  rolling_avg_usage: number | null;
  valid_lap_count: number;
  fuel_at_lap_start: number | null;
};

export type FuelProjectionSnapshot = {
  laps_remaining: number | null;
  projected_finish_fuel: number | null;
  risk_level: string;
  warning: boolean;
};

export type DriverStanding = {
  car_idx: number;
  position: number | null;
  laps: number | null;
  class_position: number | null;
  class_id: number | null;
  best_lap_time: number | null;
};

export type RaceStateData = {
  session: {
    track_name: string | null;
    session_type: string | null;
    drivers: Array<{
      car_idx: number;
      user_name: string | null;
      car_number: string | null;
    }>;
  };
  standings: {
    drivers: DriverStanding[];
  };
  player: PlayerPositionSnapshot;
  gap_ahead: GapSnapshot;
  gap_behind: GapSnapshot;
  fuel_consumption: FuelConsumptionSnapshot;
  fuel_projection: FuelProjectionSnapshot;
};

export type BridgeMessage =
  | { type: "connection"; ts: number; data: ConnectionState }
  | { type: "telemetry"; ts: number; data: Record<string, unknown> }
  | { type: "race_state"; ts: number; data: RaceStateData };
