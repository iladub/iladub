class Ping {
  ok bool
  echo string
}

function PingExtract(text: string) -> Ping {
  client Claude
  prompt #"
    Return ok=true and echo the input verbatim.
    Input: {{ text }}
    {{ ctx.output_format }}
  "#
}
