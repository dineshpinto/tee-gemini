# TEE Gemini Reference Implementation

## Installation

Uses [uv](https://docs.astral.sh/uv/)

```bash
uv python install 3.12
uv sync
```

## Local

```bash
uv run start-gemini
```

## Docker

```bash
docker build -t tee-gemini .
```

```bash
docker run --name tee-gemini tee-gemini
```

## GCP

1. Create a [Compute VM](https://console.cloud.google.com/compute/instancesAdd)
2. Set the following parameters (any parameters not mentioned should be left default):

   - Name: `tee-gemini`
   - Machine Configuration -> Compute Optimized: C2D
   - Confidential VM Service: Enable
   - Deploy Container -> Container Image: `ghcr.io/dineshpinto/tee-gemini:main`
   - Run as privileged: Check
   - Environment Variables -> All environment variables defined in your `.env`
   - Boot Disk -> Change -> Confidential Images: Container-Optimized-OS 113-18224.151.27 LTS
   - Advanced Options -> Security -> Shielded VM: Check Turn on Secure Boot

3. Click on create

## Retrieving Endorsement Keys (EKPub)

Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

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

## Within the TEE

Note: This can be performed in Ubuntu.

Install [google/go-tpm-tools](https://github.com/google/go-tpm-tools):

```bash
curl -L https://github.com/google/go-tpm-tools/releases/download/v0.4.4/go-tpm-tools_Linux_x86_64.tar.gz -o go-tpm-tools.tar.gz
tar xvf go-tpm-tools.tar.gz
```

### Get TEE PubKey

```bash
./gotpm pubkey
```

### Encrypt and Decrypt data with the TEE

```bash
./gotpm seal --input "input.txt" "sealed.txt"
```

```bash
./gotpm unseal --input "sealed.txt"
```

### Generate AR and verify with Google

```bash
./gotpm token
```
