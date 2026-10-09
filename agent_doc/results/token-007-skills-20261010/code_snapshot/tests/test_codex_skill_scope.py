import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from agent_runtime.codex_skill_scope import resolve_skill_scope,check_skill_catalog_delta

class SkillScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.paths=[]
        for name in ('required','unused','unknown','system'):
            p=self.root/name/'SKILL.md';p.parent.mkdir();p.write_text('test skill',encoding='utf-8');self.paths.append(str(p))
        self.catalog={'cwd':str(self.root),'errors':[],'skills':[{'path':p,'enabled':True,'scope':'system' if i==3 else 'user'} for i,p in enumerate(self.paths)]}
        self.contract={'schema_version':'codex-skill-scope/v1','requirements_complete':True,'required_skill_paths':self.paths[:1],'excluded_skill_paths':self.paths[1:2]}

    def test_explicit_only_and_preserve_existing(self):
        current=[{'path':self.paths[2],'enabled':False},{'path':self.paths[0],'enabled':True}]
        original=copy.deepcopy((self.contract,self.catalog,current))
        result=resolve_skill_scope(self.contract,self.catalog,current)
        self.assertEqual(result['config_overrides']['skills.config'],current+[{'path':self.paths[1],'enabled':False}])
        self.assertEqual((self.contract,self.catalog,current),original)
        self.assertNotIn(self.paths[3],str(result))

    def test_unknown_keeps_defaults_and_disabled_stays_disabled(self):
        self.contract['requirements_complete']=False
        self.assertEqual(resolve_skill_scope(self.contract,{},[])['config_overrides'],{})
        self.contract['requirements_complete']=True
        self.catalog['skills'][1]['enabled']=False
        self.assertEqual(resolve_skill_scope(self.contract,self.catalog,[])['config_overrides'],{})
        self.catalog['skills'][0]['enabled']=False
        with self.assertRaises(ValueError):resolve_skill_scope(self.contract,self.catalog,[])

    def test_fail_on_ambiguous_missing_and_required_exclusions(self):
        cases=[]
        for change in ({'excluded_skill_paths':self.paths[:1]}, {'required_skill_paths':[str(self.root/'absent'/'SKILL.md')]}, {'excluded_skill_paths':self.paths[3:]}, {'requirements_complete':1}, {'other':1}):
            c=copy.deepcopy(self.contract);c.update(change);cases.append((c,self.catalog,[]))
        bad=copy.deepcopy(self.catalog);bad['skills'].append(bad['skills'][0]);cases.append((self.contract,bad,[]))
        bad=copy.deepcopy(self.catalog);bad['errors']=[{'message':'missing'}];cases.append((self.contract,bad,[]))
        cases.append((self.contract,self.catalog,[{'path':self.paths[0],'enabled':False}]))
        cases.append((self.contract,self.catalog,[{'path':self.paths[0],'enabled':True,'extra':1}]))
        for c,b,a in cases:
            with self.subTest(c=c,b=b,a=a),self.assertRaises((OSError,ValueError)):resolve_skill_scope(c,b,a)

    def test_exact_removal_does_not_hide_permission_changes(self):
        entry='- unrelated: travel (file: r0/travel/SKILL.md)\n'
        base='<skills_instructions>\nRules stay\n### Available skills\n'+entry+'- required: code (file: r0/code/SKILL.md)\n</skills_instructions>Permissions stay\n'
        target=base.replace(entry,'')
        self.assertTrue(check_skill_catalog_delta(base,target,[entry])['remaining_plaintext_exact'])
        for text,entries in [(target.replace('Permissions stay','Permissions changed'),[entry]),(target,[entry,entry]),(target,[entry[:-1]]),(target.replace('Rules stay',''),[entry])]:
            with self.assertRaises(ValueError):check_skill_catalog_delta(base,text,entries)
        for prefix in ('> ','quoted inline: '):
            quoted=base.replace(entry,prefix+entry)
            with self.assertRaises(ValueError):check_skill_catalog_delta(quoted,quoted.replace(entry,''),[entry])
        outside=base.replace(entry,'').replace('Rules stay\n','Rules stay\n'+entry)
        with self.assertRaises(ValueError):check_skill_catalog_delta(outside,outside.replace(entry,''),[entry])

    def test_actual_cli_readonly_project_bound_and_duplicate_json(self):
        request={'project_root':str(self.root),'contract':self.contract,'catalog':self.catalog,'current_skills_config':[]}
        p=self.root/'request.json';p.write_text(json.dumps(request),encoding='utf-8')
        cli=Path(__file__).resolve().parents[1]/'scripts/codex_skill_scope.py'
        command=[sys.executable,str(cli),'--root',str(self.root),'--request','request.json']
        before={str(x.relative_to(self.root)):x.read_bytes() for x in self.root.rglob('*') if x.is_file()}
        r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(json.loads(r.stdout)['excluded_skill_paths'],self.paths[1:2])
        self.assertEqual(before,{str(x.relative_to(self.root)):x.read_bytes() for x in self.root.rglob('*') if x.is_file()})
        request['project_root']=str(self.root/'required');p.write_text(json.dumps(request),encoding='utf-8')
        self.assertEqual(subprocess.run(command,capture_output=True).returncode,1)
        p.write_text('{"project_root":1,"project_root":2}',encoding='utf-8')
        self.assertEqual(subprocess.run(command,capture_output=True).returncode,1)

if __name__=='__main__':unittest.main()
