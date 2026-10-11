import importlib.util
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

spec=importlib.util.spec_from_file_location('planner',Path(__file__).resolve().parents[2]/'modules/workflow/messaging/planner.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Messaging(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.p=m.Planner(self.root)
    def approve(self,revision=0,recipients=None,key='approve'):
        return self.p.change('channel.save',dict(key=key,channel='email',revision=revision,senders=['known@example.invalid'],recipients=['recipient@example.invalid'] if recipients is None else recipients),now=1000)
    def rule(self,key='rule'):
        return self.p.change('rule.create',dict(key=key,channel='email',recipient='recipient@example.invalid',topic='Water report',content='Owner-authored fixed text.',period=3600,firstDue=1000),now=1000)
    def test_sender_filter_default_deny_exact_and_not_retained(self):
        self.assertFalse(self.p.check_sender(dict(channel='email',sender='known@example.invalid'))['allowed']);self.approve()
        self.assertTrue(self.p.check_sender(dict(channel='email',sender='known@example.invalid'))['allowed'])
        self.assertFalse(self.p.check_sender(dict(channel='email',sender='Known@example.invalid'))['allowed'])
        self.assertEqual(self.p.snapshot()['drafts'],[])
        with self.assertRaises(m.Invalid):self.p.check_sender(dict(channel='email',sender='Display Name <known@example.invalid>'))
    def test_recipient_approval_is_required(self):
        with self.assertRaises(m.Invalid):self.rule()
        self.approve();self.rule();self.assertEqual(len(self.p.snapshot()['rules']),1)
    def test_idempotency_and_revision_conflicts(self):
        a=self.approve();self.assertEqual(self.approve(),a)
        with self.assertRaises(m.Conflict):self.approve(recipients=[],key='approve')
        with self.assertRaises(m.Conflict):self.approve(key='stale')
        self.assertEqual(self.rule(),self.rule());self.assertEqual(len(self.p.snapshot()['rules']),1)
    def test_concurrent_ticks_create_one_draft(self):
        self.approve();self.rule()
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda _:self.p.tick(1000),range(8)))
        self.assertEqual(len(self.p.snapshot()['drafts']),1);self.assertEqual(self.p.snapshot()['rules'][0]['next_due'],4600)
    def test_restart_and_downtime_coalesce_without_duplicates(self):
        self.approve();self.rule();self.p.tick(1000);self.p=m.Planner(self.root)
        self.p.tick(1000+3600*10+30);self.p.tick(1000+3600*10+30)
        drafts=self.p.snapshot()['drafts'];self.assertEqual(len(drafts),2);self.assertEqual(drafts[0]['due'],37000)
    def test_removal_pauses_and_reapproval_does_not_resume(self):
        self.approve();rule=self.rule();self.approve(1,[],key='remove');self.p.tick(1000)
        self.assertEqual(self.p.snapshot()['drafts'],[])
        with self.assertRaises(m.Invalid):self.p.change('rule.pause',dict(key='badresume',id=rule['id'],revision=2,paused=False),now=1000)
        self.approve(2,key='reapprove');self.p.tick(1000);self.assertEqual(self.p.snapshot()['drafts'],[])
        self.p.change('rule.pause',dict(key='resume',id=rule['id'],revision=2,paused=False),now=1000);self.p.tick(1000)
        self.assertEqual(len(self.p.snapshot()['drafts']),1)
    def test_pause_preserves_existing_drafts(self):
        self.approve();rule=self.rule();self.p.tick(1000)
        self.p.change('rule.pause',dict(key='pause',id=rule['id'],revision=1,paused=True),now=1001);self.p.tick(4600)
        self.assertEqual(len(self.p.snapshot()['drafts']),1)
    def test_unknown_schema_is_refused(self):
        with self.p.db() as db:db.execute('PRAGMA user_version=99')
        with self.assertRaises(m.Invalid):m.Planner(self.root)
    def test_content_preserved_and_invalid_interval_refused(self):
        self.approve()
        payload=dict(key='exact',channel='email',recipient='recipient@example.invalid',topic='Test',content='  literal text\n',period=3600,firstDue=1000)
        self.p.change('rule.create',payload,now=1000);self.p.tick(1000)
        self.assertEqual(self.p.snapshot()['drafts'][0]['content'],payload['content'])
        payload.update(key='invalid-interval',period=1)
        with self.assertRaises(m.Invalid):self.p.change('rule.create',payload,now=1000)

    def test_limits_and_retention(self):
        with self.assertRaises(m.Invalid):self.p.change('channel.save',dict(key='oversize',channel='email',revision=0,senders=['a']*51,recipients=[]))
        self.approve();self.rule()
        for slot in range(205):self.p.tick(1000+slot*3600)
        with self.p.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM drafts').fetchone()[0],200)
        self.assertEqual(len(self.p.snapshot()['drafts']),50)

if __name__=='__main__':unittest.main()
