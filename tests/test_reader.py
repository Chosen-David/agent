"""Behavioral checks for PDF page identity, notes binding and inert HTML data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import fitz

SCRIPT=Path(__file__).resolve().parents[1]/'plugins/research-assistant/skills/paper-reading-companion/scripts/build_reader.py'
spec=importlib.util.spec_from_file_location('reader', SCRIPT)
reader=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

class ReaderChecks(unittest.TestCase):
    def test_page_ranges(self):
        self.assertEqual(reader.parse_pages('1-3,2,7', 9), [1,2,3,7])
        self.assertEqual(reader.parse_pages(None, 30), list(range(1,21)))
        for bad in ('0','3-1','10','1-2-3'):
            with self.assertRaises(ValueError): reader.parse_pages(bad, 9)

    def test_render_and_untrusted_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);pdf=tmp/'fixture.pdf';out=tmp/'reader.html';notes=tmp/'notes.json'
            doc=fitz.open()
            for i in (1,2):
                page=doc.new_page();page.insert_text((72,72),f'Synthetic fixture, physical page {i}')
            doc.save(pdf);doc.close()
            digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
            hostile='</script><script>window.injected=true</script>'
            notes.write_text(json.dumps({'paper_sha256':digest,'cards':[{'id':'EXPL-1','page':2,'anchor':'test','question':'fixture only','answer':hostile,'sources':[{'label':'test','url':'javascript:alert(1)'}]}]}))
            command=[sys.executable,str(SCRIPT),str(pdf),'--out',str(out),'--pages','2','--notes',str(notes)]
            result=subprocess.run(command,capture_output=True,text=True,check=True)
            meta=json.loads(result.stdout);self.assertEqual(meta['rendered_pages'],[2]);self.assertFalse(meta['live_chat_backend'])
            text=out.read_text();self.assertNotIn(hostile,text)
            data=json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>',text,re.S).group(1))
            self.assertEqual(data['pages'][0]['number'],2);self.assertEqual(data['sha256'],digest)
            self.assertIn('physical page 2',data['pages'][0]['text']);self.assertTrue(data['pages'][0]['image'])
            self.assertEqual(data['cards'][0]['answer'],hostile)
            # Identity mismatch must fail, instead of attaching another paper's answers.
            notes.write_text(json.dumps({'paper_sha256':'wrong','cards':[]}))
            bad=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0);self.assertIn('SHA-256',bad.stderr)
            # Refuse destructive output paths.
            bad=subprocess.run([sys.executable,str(SCRIPT),str(pdf),'--out',str(pdf)],capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0);self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(),digest)

if __name__=='__main__':unittest.main()
