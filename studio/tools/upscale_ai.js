// AI x2/x4 upscale with UpscalerJS ESRGAN-thick (tfjs-node), ONLY for photos photo_check.py marks UPSCALE (P17).
// One-time install (per session):  mkdir -p /tmp/claude-0/up && cd /tmp/claude-0/up && npm init -y >/dev/null &&
//   npm i @tensorflow/tfjs-node upscaler @upscalerjs/esrgan-thick
// usage: node studio/tools/upscale_ai.js <scale 2|4> <in.jpg> <out.png>
// Best result (oak living room 13.10): x4, then area-downscale to x2 (keeps edges/grain, drops x4 artefacts);
// compare mean Lab to the source (shift < 1) so the natural colours stay (P15).
const path = require('path');
const r = require('module').createRequire('/tmp/claude-0/up/x.js');
const tf = r('@tensorflow/tfjs-node');
const Upscaler = r('upscaler/node');
const fs = require('fs');
(async () => {
  const [sc, inp, out] = process.argv.slice(2);
  const model = r('@upscalerjs/esrgan-thick/' + sc + 'x');
  const up = new Upscaler({ model });
  const img = tf.node.decodeImage(fs.readFileSync(inp), 3);
  const t0 = Date.now();
  const res = await up.upscale(img, { output: 'tensor', patchSize: 128, padding: 8 });
  const u8 = tf.cast(tf.clipByValue(tf.round(res), 0, 255), 'int32');
  fs.writeFileSync(out, await tf.node.encodePng(u8));
  console.log(out, res.shape, ((Date.now() - t0) / 1000).toFixed(1) + 's');
})();
