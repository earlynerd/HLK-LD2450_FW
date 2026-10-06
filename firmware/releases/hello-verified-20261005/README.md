# Bench-verified hello image

This preserves the exact `hello-repeat` image installed on October 5, 2026
(Pacific time), before the three-second recovery-window source change.
It is a historical working binary, not an image built from the current source.

- UFW SHA256: `05fafed95ed20aba1400bbeae2884a054d9716edae345850e02ceff23c4b1edb`.
- PA9 build banner: `setup_arch Oct 5 2026 19:47:06` (spacing varies).
- Module UART: PA1 TX / PA0 RX, 256000 baud; PA9 debug: 115200 baud.
- Hello only; radar held off. UART updater remains available during the hello loop.
- Custom updater installed this distinct image in 417 reads with 184320 reported
  update bytes, final success, the new banner and 12 heartbeats in 12 seconds.
- The preceding same-source hello-logfix image also passed stock installation
  and a user-confirmed power-cycle boot. The final hello-repeat image was observed
  after its update reset; it was not separately power-cycled in that bench run.

The build and patch manifests preserve original source/tool hashes and local
build paths. `sdk.elf` permits later symbolization against the exact tested code.
The UFW contains third-party vendor components; repository provenance notices
apply. Filesystem/configuration warnings remain unresolved. Stock restoration,
radar operation and the later recovery-window change are not qualified here.

See [bench evidence](../../../output/firmware_build/hello_hardware_validation_20261005.json)
and [current build instructions](../../docs/IMAGE_BUILD.md).
