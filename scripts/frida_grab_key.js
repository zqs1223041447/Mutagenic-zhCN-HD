'use strict';
// Grab Godot script encryption key at runtime.
// Strategy: find "GDEC" string in .rdata, find rip-relative refs in .text,
// backtrace to function start, hook it, dump rdx (Vector<uint8_t>& key).

const mod = Process.getModuleByName("Mutagenic.exe");
const base = mod.base;
const sections = mod.enumerateSections();
let text = sections.find(s => s.name === '.text');
let rdata = sections.find(s => s.name === '.rdata' || s.name === '.rodata' || s.name === '.data');
if (!rdata) rdata = sections.find(s => s.name === '_RDATA');
console.log('base=' + base + ' size=' + mod.size);
console.log('text=' + (text ? text.address + ' size=' + text.size : 'NONE'));
console.log('rdata=' + (rdata ? rdata.address + ' size=' + rdata.size : 'NONE'));

// 1. find GDEC strings in rdata
let gdecs = [];
if (rdata) {
    const matches = Memory.scanSync(rdata.address, rdata.size, '47 44 45 43');
    gdecs = matches.map(m => m.address);
}
console.log('GDEC in rdata: ' + gdecs.length);

// 2. find rip-relative refs in .text
const refs = [];
if (text && gdecs.length) {
    const targetSet = new Set(gdecs.map(a => a.toString()));
    const bytes = new Uint8Array(text.address.readByteArray(text.size));
    for (let i = 0; i + 7 < bytes.length; i++) {
        if (bytes[i] === 0x48 && (bytes[i + 1] === 0x8d || bytes[i + 1] === 0x8b) &&
            (bytes[i + 2] & 0xC7) === 0x05) {
            const disp = (bytes[i + 3] | (bytes[i + 4] << 8) | (bytes[i + 5] << 16) | (bytes[i + 6] << 24)) | 0;
            const target = text.address.add(i + 7 + disp);
            if (targetSet.has(target.toString())) {
                refs.push(text.address.add(i));
            }
        }
    }
}
console.log('text refs to GDEC: ' + refs.length);
refs.forEach(r => console.log('  ref at ' + r));

// 3. backtrace to function start (find prologue)
function findFunctionStart(addr) {
    let p = addr.sub(1);
    for (let i = 0; i < 0x4000; i++) {
        const b = p.readU8();
        if (b === 0xCC || b === 0x90) {
            // check if next looks like prologue
            const nb = p.add(1).readU8();
            if (nb === 0x55 || nb === 0x40 || nb === 0x48 || nb === 0x53 || nb === 0x56 || nb === 0x57 ||
                nb === 0x41 || nb === 0x4C) {
                return p.add(1);
            }
        }
        p = p.sub(1);
    }
    return addr;
}

// 4. hook candidates; dump rdx as Vector<uint8_t>
const hooked = new Set();
let keyFound = null;
refs.forEach(ref => {
    const fn = findFunctionStart(ref);
    if (hooked.has(fn.toString())) return;
    hooked.add(fn.toString());
    console.log('hooking ' + fn);
    try {
        Interceptor.attach(fn, {
            onEnter(args) {
                const v = this.context.rdx;
                try {
                    const p = v.readPointer();
                    const n = v.add(8).readU32();
                    if (n === 32) {
                        const keyBytes = new Uint8Array(p.readByteArray(32));
                        if (!keyFound) {
                            keyFound = keyBytes;
                            send({ type: 'key', hex: Buffer.from(keyBytes).toString('hex') });
                        }
                    }
                } catch (e) { }
            }
        });
    } catch (e) {
        console.log('hook failed: ' + e);
    }
});

if (!refs.length) {
    send({ type: 'error', msg: 'no refs found' });
}
