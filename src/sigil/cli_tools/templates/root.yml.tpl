root:
  name: {}
  script: root
  script_dir: scripts
  args:
    - name: name
      help: your name
    - name: --shout
      action: store_true
      help: Increase volume
    - name:
        - --verbose
        - -v
      action: store_true
      help: increase verbosity