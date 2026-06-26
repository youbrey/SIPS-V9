{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.xorg.xorgserver
    pkgs.x11vnc
    pkgs.fluxbox
    pkgs.git
  ];
}
