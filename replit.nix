{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.xorg.xorgserver
    pkgs.x11vnc
    pkgs.fluxbox
    pkgs.git
  ];
}
