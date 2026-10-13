// AI x2/x4 upscale with UpscalerJS ESRGAN-thick (tfjs-node). usage: node up.js <scale 2|4> <in.jpg> <out.png>
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
