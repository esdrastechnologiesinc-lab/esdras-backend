const functions = require('firebase-functions');
const admin = require('firebase-admin');
const axios = require('axios');

admin.initializeApp();
const db = admin.firestore();

const REPLICATE_TOKEN = functions.config().replicate.token; 
';

exports.renderHair = functions.https.onCall(async (data, context) => {
  if (!context.auth) throw new functions.https.HttpsError('unauthenticated', 'Login required');
  const { headImageUrl, hairstyleImageUrl, hairType = 'coiled' } = data;
  if (!headImageUrl || !hairstyleImageUrl) throw new functions.https.HttpsError('invalid-argument', 'Missing images');

  try {
    const res = await axios.post('https://api.replicate.com/v1/predictions', {
      version: "cjwbw/style-your-hair:8f6b8e4e4b4e4b4e4b4e4b4e4b4e4b4e",
      input: {
        image: headImageUrl,
        prompt: `Ultra-realistic ${hairType} hair with physics, natural bounce and flow, perfect on African/Caucasian skin, 8k`,
        hair_type: hairType,
        enable_physics: true,
        strength: 0.88,
        guidance_scale: 8.0
      }
    }, { headers: { Authorization: `Token ${REPLICATE_TOKEN}` } });

    const id = res.data.id;
    let result;
    for (let i = 0; i < 40; i++) {
      await new Promise(r => setTimeout(r, 3000));
      const poll = await axios.get(`https://api.replicate.com/v1/predictions/${id}`, {
        headers: { Authorization: `Token ${REPLICATE_TOKEN}` }
      });
      if (poll.data.status === 'succeeded') { result = poll.data.output[0]; break; }
      if (poll.data.status === 'failed') throw new Error('Failed');
    }

    if (!result) throw new Error('Timeout');

    await db.collection('renders').add({
      userId: context.auth.uid,
      headImage: headImageUrl,
      styleImage: hairstyleImageUrl,
      resultUrl: result,
      hairType,
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    });

    return { success: true, renderedImage: result };
  } catch (e) {
    throw new functions.https.HttpsError('internal', 'Render failed');
  }
});
