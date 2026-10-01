# @angysguard/windows-agent (experimental)

This is the npm-distributed foundation for a fixed-command Windows terminal agent.

This package is publishable but has **not** been published to npm yet. Until a
signed npm release exists, test it from a source checkout:

```powershell
npm install -g .\packages\windows-agent
angysguard status
angysguard lock
```

After publication, the launcher install will be:

```powershell
npm install -g @angysguard/windows-agent
```

It currently provides only an explicit local Windows lock command and clear
capability status. It does not yet provide background protection, camera/input
monitoring, remote commands, shell execution, or Windows release support.
