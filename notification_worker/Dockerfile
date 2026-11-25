FROM elixir:1.20.2-otp-28 AS build
WORKDIR /app
RUN mix local.hex --force && mix local.rebar --force
COPY notification_worker/mix.exs notification_worker/mix.lock ./
RUN MIX_ENV=prod mix deps.get --only prod && MIX_ENV=prod mix deps.compile
COPY notification_worker/lib ./lib
RUN MIX_ENV=prod mix release

FROM elixir:1.20.2-otp-28
WORKDIR /app
COPY --from=build /app/_build/prod/rel/leave_flow_worker ./
CMD ["/app/bin/leave_flow_worker", "start"]
