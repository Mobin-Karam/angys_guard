# @angysguard/windows-agent (experimental)

This is the npm-distributed foundation for a fixed-command Windows terminal agent.

Use the source package while developing or testing the wrapper:

```powershell
npm install -g .\packages\windows-agent
angysguard status
angysguard lock
```

The public package install is:

```powershell
npm install -g @angysguard/windows-agent
```

It currently provides only an explicit local Windows lock command and clear
capability status. It does not yet provide background protection, camera/input
monitoring, remote commands, shell execution, or Windows release support. Its
`1.0.1` package version identifies the stable wrapper interface only; it does
not change AngysGuard's Windows support status.
