# TEE Gemini Reference Implementation

## Run Locally

```bash
docker run --name tee-gemini tee-gemini
```

## Run on GCP

### Using gcloud CLI

```bash
gcloud compute instances create-with-container tee-gemini-testing \
    --project=flare-network-sandbox \
    --zone=us-central1-a \
    --machine-type=c2d-standard-2 \
    --network-interface=network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=TERMINATE \
    --provisioning-model=STANDARD \
    --service-account=83674517876-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=https-server \
    --confidential-compute \
    --image=projects/cos-cloud/global/images/cos-stable-113-18244-151-50 \
    --boot-disk-size=10GB \
    --boot-disk-type=pd-standard \
    --boot-disk-device-name=tee-gemini-testing \
    --container-image=docker\ \
pull\ ghcr.io/dineshpinto/tee-gemini:main \
    --container-restart-policy=always \
    --container-privileged \
    --container-env=GEMINI_ENDPOINT_ADDRESS=,RPC_URL=,SECONDS_BW_ITERATIONS=,TEE_ADDRESS=,TEE_PRIVATE_KEY=,GEMINI_API_KEY= \
    --shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud,container-vm=cos-stable-113-18244-151-50 \
    --confidential-compute
```

### Using Console

1. Create a [Compute VM](https://console.cloud.google.com/compute/instancesAdd)
2. Set the following parameters (any parameters not mentioned should be left default):

   - Name: `tee-gemini`
   - Machine Configuration -> Compute Optimized: C2D
   - Confidential VM Service: Enable
   - Deploy Container -> Container Image: `ghcr.io/dineshpinto/tee-gemini:main`
   - Run as privileged: Check
   - Environment Variables -> All environment variables defined in `.env.example`
   - Boot Disk -> Change -> Confidential Images: Container-Optimized-OS 113-18224.151.27 LTS
   - Advanced Options -> Security -> Shielded VM: Check Turn on Secure Boot

3. Click on Create

## Query Gemini API onchain

1. Call `makeRequest` with `_data` as the query to Gemini.

2. Query `getLatestResponse` which returns a `struct Response` with the Gemini response text and metadata.

## Query and verify attestation token

1. Call `requestOIDCToken`.

2. See `data` parameter of `OIDCRequestFullfilled` event raised in `fulfillOIDCToken` (callback) transaction.

3. Use the output of the `data` parameter from the last step.

   ```bash
   uv run verify-token --token <TOKEN>
   ```

## Build

Uses [uv](https://docs.astral.sh/uv/).

Install dependencies

```bash
uv python install 3.12
uv sync
```

Build container

```bash
docker build -t tee-gemini .
```

Run local development server

```bash
uv run start-gemini
```

## Retrieving Endorsement Keys (EKPub)

You can retrieve the endorsement key for both the encryption key and the signing key. You can use the encryption key to encrypt data so that only the vTPM can read it, or the signing key to verify signatures that the vTPM makes. You can also use the key to ascertain the identity of a VM instance before sending sensitive information to it.

```bash
gcloud compute instances get-shielded-identity tee-gemini --zone us-central1-a
```

### Inspect the TEE encryption and signing keys

```bash
gcloud compute instances get-shielded-identity tee-gemini --zone us-central1-a --format=json | jq -r '.encryptionKey.ekCert' > ekcert.pem
openssl x509 -in ekcert.pem -text -noout
```

```bash
gcloud compute instances get-shielded-identity tee-gemini --zone us-central1-a --format=json | jq -r '.signingKey.ekCert' > akcert.pem
openssl x509 -in akcert.pem -text -noout
```
