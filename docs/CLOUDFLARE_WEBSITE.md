# Cloudflare website setup

Lemonade Store ships every business with a small public website. The
website is **public**; the local store database is **private**. Only
owner-approved content leaves the local system.

Default stack:

- static site
- GitHub repository
- Cloudflare Pages (hosting)
- Cloudflare DNS
- Cloudflare Turnstile (form protection)

## Required pages

| Slug | Title |
| --- | --- |
| `home` | Store name + one-line description |
| `products` | Categories and featured products |
| `soil` | Soil availability (Tie Dye Farms specific; other stores can omit) |
| `hours-location` | Hours of operation and address |
| `contact` | Contact form or instructions |
| `privacy` | Privacy and local-data statement |
| `promotions` | Owner-approved promotion landing pages |

## Step-by-step launch path

1. **Create a Cloudflare account** for the business.
2. **Add the store domain to Cloudflare DNS.** Update the registrar's
   nameservers to Cloudflare's.
3. **Create a website repository** (e.g. `tiedye-farms-site`).
4. **Build a static website.** A flat HTML/CSS site is enough for v0.1.
5. **In the Cloudflare dashboard, open Workers & Pages** and create a
   new Pages project.
6. **Connect the GitHub repository** to the Pages project.
7. **Choose the production branch** (`main` by default).
8. **Configure the build command and output directory** for the chosen
   static site generator. For a plain HTML site, build command is empty
   and output is the repo root.
9. **Deploy the first build.**
10. **Add the custom domain** in the Pages project. The custom domain
    must be on the same Cloudflare account as the Pages project.
11. **Confirm HTTPS** is on. Cloudflare provisions a cert automatically.
12. **Add Turnstile** to any contact or request form to protect against
    spam without a traditional CAPTCHA.
13. **Document the owner's edit workflow.** A typical loop:

```text
inventory update
   ↓
marketeer drafts site/social copy → marketing.site_update.drafted
   ↓
owner approves → marketing.post.approved
   ↓
site department writes the change to the website repo → site.change.approved
   ↓
Cloudflare Pages deploys → site.deploy.completed
```

## References

- [Cloudflare Pages](https://pages.cloudflare.com/)
- [Cloudflare Pages — custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/)

## Boundary

The website is the only Cloudflare-required surface. Cashier, CIT,
accounting, inventory, and reports never depend on Cloudflare to
function.
