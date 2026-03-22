let
  pkgs = import (fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-25.11.tar.gz";
  }) {};
in
pkgs.mkShell {
  buildInputs = [
    pkgs.gst_all_1.gstreamer
  ];
  packages = [
    (pkgs.python313.withPackages (python-pkgs: with python-pkgs; [
      flask
      sqlalchemy
      flask-sqlalchemy
      opencv-python-headless
      ultralytics
    ]))
  ];
}